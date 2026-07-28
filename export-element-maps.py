"""
Batch export geochemical element maps (IDW raster + point layer) to GeoTIFF.
Run this INSIDE ArcGIS Pro's Python window, or via arcpy in a script tool,
so it has access to the current project (aprx).

Assumes:
  - A layout named LAYOUT_NAME already exists with:
      * main map frame containing all IDW_<elem> rasters + <elem>_mgkg point layers
      * inset map frame containing andros_geology (legend only, grid on left/bottom only)
  - Raster layers are named "IDW_<Element>" e.g. IDW_As, IDW_Zn
  - Point layers are named "<Element>_mgkg" e.g. As_mgkg, Zn_mgkg
    (EDIT raster_name()/point_name() below if your naming differs)
"""

import arcpy
import os

# ---------------------------------------------------------------------
# CONFIG - edit these to match your project
# ---------------------------------------------------------------------
LAYOUT_NAME = "Element_Layout"          # name of the layout in your aprx
MAIN_MAP_FRAME_NAME = "Map Frame"       # main geochemical map frame name in layout
INSET_MAP_FRAME_NAME = "Map Frame 2"    # geology inset map frame name in layout (static, andros_geology)
OUT_FOLDER = r"C:\Users\nick\Desktop\arcgis_pro_prjects\ANDOS_AVGOUSTATOS\map_tiffs"

# Names of the static layout elements you placed manually. These don't change
# per element - they're just validated here so a missing one raises a clear
# error instead of silently exporting an incomplete map. Set to None to skip
# checking a given element if you didn't name it / don't want it checked.
LEGEND_NAME = "Legend"          # e.g. "Legend" - main map legend (below main map)
INSET_LEGEND_NAME = "Legend_1"    # e.g. "Legend 2" - geology inset legend
NORTH_ARROW_NAME = "North_Arrow"     # e.g. "North Arrow" - ArcGIS North 2, top-left of main map
SCALE_BAR_NAME = "Dual_Scale_Bar"       # e.g. "Scale Bar" - Feet and Meters dual scale bar

# Full element list, As -> Zn, matching your Drawing Order screenshot
ELEMENTS = [
    "As", "Ba", "Ca", "Cr", "Cu", "Fe", "Mn", "Ni",
    "Pb", "Rb", "Sr", "Ti", "V", "Zn"
    # add any missing elements from your full As->Zn list here
]

def raster_name(elem):
    return f"IDW_{elem}"

def point_name(elem):
    return f"{elem}_mgkg"

# ---------------------------------------------------------------------

def get_map_and_layers(main_map):
    """Return dict {layer_name: layer} for the main map, all layers."""
    return {lyr.name: lyr for lyr in main_map.listLayers()}


def check_static_elements(layout):
    """
    Validate that the static layout elements (legend, inset legend, north
    arrow, scale bar, inset map frame) exist before running the export loop.
    These elements don't change per-element - they're placed once manually -
    so this just catches a missing/misnamed element early with a clear error
    instead of exporting 14 GeoTIFFs that are all missing the same piece.
    """
    checks = [
        ("MAPFRAME_ELEMENT", INSET_MAP_FRAME_NAME, "geology inset map frame"),
        ("LEGEND_ELEMENT", LEGEND_NAME, "main legend"),
        ("LEGEND_ELEMENT", INSET_LEGEND_NAME, "inset legend"),
        ("MAPSURROUND_ELEMENT", NORTH_ARROW_NAME, "north arrow"),
        ("MAPSURROUND_ELEMENT", SCALE_BAR_NAME, "scale bar"),
    ]

    for elem_type, name, label in checks:
        if name is None:
            continue  # skip check - not named / not being validated
        found = layout.listElements(elem_type, name)
        if not found:
            available = [e.name for e in layout.listElements(elem_type)]
            raise ValueError(
                f"No {label} named '{name}' found in layout '{layout.name}'. "
                f"Available {elem_type} elements: {available}. "
                f"Update the corresponding *_NAME variable in CONFIG, "
                f"or set it to None to skip this check."
            )

def main():
    aprx = arcpy.mp.ArcGISProject("CURRENT")

    matching_layouts = aprx.listLayouts(LAYOUT_NAME)
    if not matching_layouts:
        available = [l.name for l in aprx.listLayouts()]
        raise ValueError(
            f"No layout named '{LAYOUT_NAME}' found. "
            f"Available layouts: {available}. "
            f"Update LAYOUT_NAME in the CONFIG section to match one of these."
        )
    layout = matching_layouts[0]

    matching_frames = layout.listElements("MAPFRAME_ELEMENT", MAIN_MAP_FRAME_NAME)
    if not matching_frames:
        available = [e.name for e in layout.listElements("MAPFRAME_ELEMENT")]
        raise ValueError(
            f"No map frame named '{MAIN_MAP_FRAME_NAME}' found in layout '{LAYOUT_NAME}'. "
            f"Available map frames: {available}. "
            f"Update MAIN_MAP_FRAME_NAME in the CONFIG section to match one of these."
        )
    mf = matching_frames[0]
    main_map = mf.map
    layers_by_name = get_map_and_layers(main_map)

    check_static_elements(layout)

    if not os.path.exists(OUT_FOLDER):
        os.makedirs(OUT_FOLDER)

    for elem in ELEMENTS:
        rname = raster_name(elem)
        pname = point_name(elem)

        r_lyr = layers_by_name.get(rname)
        p_lyr = layers_by_name.get(pname)

        if r_lyr is None:
            arcpy.AddWarning(f"Raster layer '{rname}' not found - skipping raster for {elem}")
        if p_lyr is None:
            arcpy.AddWarning(f"Point layer '{pname}' not found - skipping points for {elem}")

        # Turn everything relevant OFF first, then turn on only this element's layers
        for name, lyr in layers_by_name.items():
            if name.startswith("IDW_") or name.endswith("_mgkg"):
                lyr.visible = False

        if r_lyr is not None:
            r_lyr.visible = True
        if p_lyr is not None:
            p_lyr.visible = True

        # Optional: update a title text element if you have one named "Title"
        title_elems = layout.listElements("TEXT_ELEMENT", "Title")
        if title_elems:
            title_elems[0].text = f"{elem} - Geochemical Distribution"

        out_path = os.path.join(OUT_FOLDER, f"{elem}_map.tif")

        layout.exportToTIFF(
            out_path,
            resolution=300,
            geoTIFF_tags=True,
            color_mode="24-BIT_TRUE_COLOR"
            # all other params left at default
        )

        arcpy.AddMessage(f"Exported {out_path}")

    arcpy.AddMessage("Done - all element maps exported.")

if __name__ == "__main__":
    main()
