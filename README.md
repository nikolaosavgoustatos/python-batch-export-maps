# Batch Geochemical Map Export (ArcGIS Pro)

## Overview

This Python script automates the export of geochemical element maps from an ArcGIS Pro project.

For each element, the script:

* Displays only the corresponding IDW interpolation raster.
* Displays only the corresponding sample point layer.
* Updates the map title (optional).
* Keeps all static layout components unchanged (north arrow, legends, scale bar, geology inset, etc.).
* Exports the layout as a georeferenced GeoTIFF.

This eliminates the need to manually enable and disable layers before exporting each map.

---

# Requirements

* ArcGIS Pro
* Python environment included with ArcGIS Pro (`arcpy`)
* A project containing:

  * A layout configured for map export
  * IDW raster layers
  * Sample point layers

The script **must be executed inside ArcGIS Pro**, either:

* From the Python Window
* As a Script Tool
* Using `ArcGISProject("CURRENT")`

It cannot be executed from a normal Python installation.

---

# Expected Project Structure

## Layout

A layout named:

```
Element_Layout
```

(or change `LAYOUT_NAME` in the configuration section)

The layout should already contain:

* Main map frame
* Geology inset map frame
* Main legend
* Inset geology legend
* North arrow
* Scale bar
* Title (optional)

These layout elements remain fixed throughout the export process.

---

## Map Frames

Main map frame:

```
Map Frame
```

Inset map frame:

```
Map Frame 2
```

If your project uses different names, modify:

```python
MAIN_MAP_FRAME_NAME
INSET_MAP_FRAME_NAME
```

---

## Raster Layers

Each interpolation raster should follow this naming convention:

```
IDW_As
IDW_Ba
IDW_Ca
...
IDW_Zn
```

The helper function controlling this is

```python
def raster_name(elem):
    return f"IDW_{elem}"
```

Modify this function if your raster naming differs.

---

## Point Layers

Each sample layer should be named

```
As_mgkg
Ba_mgkg
Ca_mgkg
...
Zn_mgkg
```

Controlled by

```python
def point_name(elem):
    return f"{elem}_mgkg"
```

---

# Supported Elements

The default list is

```
As
Ba
Ca
Cr
Cu
Fe
Mn
Ni
Pb
Rb
Sr
Ti
V
Zn
```

Additional elements can simply be added to the `ELEMENTS` list.

---

# Output

GeoTIFF files are written to

```
C:\Users\nick\Desktop\arcgis_pro_prjects\ANDOS_AVGOUSTATOS\map_tiffs
```

Each exported file is named

```
As_map.tif
Ba_map.tif
...
Zn_map.tif
```

---

# Export Settings

The script exports:

* Format: GeoTIFF
* Resolution: 300 dpi
* Color Mode: 24-bit True Color
* GeoTIFF Tags: Enabled

Example:

```python
layout.exportToTIFF(
    out_path,
    resolution=300,
    geoTIFF_tags=True,
    color_mode="24-BIT_TRUE_COLOR"
)
```

---

# Optional Dynamic Title

If a text element named

```
Title
```

exists in the layout, it is automatically updated.

Example:

```
As - Geochemical Distribution
```

If no such text element exists, the export proceeds normally.

---

# Static Layout Validation

Before exporting, the script verifies that required layout components exist.

These checks help prevent exporting incomplete maps due to missing or incorrectly named layout elements.

The following variables control validation:

```python
LEGEND_NAME
INSET_LEGEND_NAME
NORTH_ARROW_NAME
SCALE_BAR_NAME
```

If set to `None`, the corresponding validation is skipped.

---

# Layer Visibility Workflow

For each element, the script:

1. Turns off every layer beginning with `IDW_`.
2. Turns off every layer ending with `_mgkg`.
3. Turns on only:

   * the selected IDW raster
   * the selected point layer
4. Updates the title (optional).
5. Exports the layout.
6. Repeats for the next element.

No manual interaction is required.

---

# Error Handling

The script checks for:

* Missing layout
* Missing map frame
* Missing inset map frame
* Missing legends
* Missing north arrow
* Missing scale bar
* Missing raster layers
* Missing point layers

Missing rasters or point layers generate warnings and the script continues with the remaining elements.

Missing required layout components generate descriptive errors before any exports begin.

---

# Customization

Common settings are located near the top of the script.

### Layout

```python
LAYOUT_NAME
```

### Main Map Frame

```python
MAIN_MAP_FRAME_NAME
```

### Inset Map Frame

```python
INSET_MAP_FRAME_NAME
```

### Output Folder

```python
OUT_FOLDER
```

### Elements

```python
ELEMENTS
```

### Raster Naming

```python
raster_name()
```

### Point Naming

```python
point_name()
```

---

# Typical Workflow

1. Generate all IDW rasters.
2. Add all rasters to the main map.
3. Add all point layers.
4. Design the layout once.
5. Configure the script.
6. Run the script from ArcGIS Pro.
7. Retrieve all exported GeoTIFF maps from the output folder.

This workflow ensures consistent cartographic formatting across all geochemical element maps while greatly reducing manual effort during map production.
