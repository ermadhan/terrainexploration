import os
import webbrowser
import xml.etree.ElementTree as ET
import leafmap

vrt_path = os.path.abspath(r"D:\code\terrainexploration\SRTM_GL1_srtm.vrt")

# 1. Parse the VRT XML metadata
tree = ET.parse(vrt_path)
root = tree.getroot()

# Extract the 6-parameter GDAL GeoTransform:
# [origin_x, pixel_width, rot_x, origin_y, rot_y, pixel_height]
gt_text = root.find("GeoTransform").text.strip()
gt = [float(x.strip()) for x in gt_text.split(",")]
origin_x, px_w, rot_x, origin_y, rot_y, px_h = gt

# 2. Extract every tile's DstRect and convert pixel bounds to geographic coordinates
features = []
for source in root.findall(".//VRTRasterBand[1]/*"):
    if source.tag not in ("SimpleSource", "ComplexSource"):
        continue

    dst_rect = source.find("DstRect")
    filename_el = source.find("SourceFilename")
    if dst_rect is None or filename_el is None:
        continue

    x_off = float(dst_rect.attrib["xOff"])
    y_off = float(dst_rect.attrib["yOff"])
    x_size = float(dst_rect.attrib["xSize"])
    y_size = float(dst_rect.attrib["ySize"])

    # Calculate geographic bounding box
    min_lon = origin_x + x_off * px_w
    max_lon = origin_x + (x_off + x_size) * px_w
    max_lat = origin_y + y_off * px_h
    min_lat = origin_y + (y_off + y_size) * px_h

    tile_name = os.path.basename(filename_el.text.strip())

    features.append({
        "type": "Feature",
        "properties": {
            "tile": tile_name,
            "bounds": f"[{min_lon:.2f}, {min_lat:.2f}, {max_lon:.2f}, {max_lat:.2f}]",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, max_lat],
                [min_lon, max_lat],
                [min_lon, min_lat],
            ]],
        },
    })

print(f"Extracted {len(features)} tile bounding boxes from VRT.")

geojson_data = {
    "type": "FeatureCollection",
    "features": features,
}

# Initialize the map normally, then clear the default OpenStreetMap layer
m = leafmap.Map(center=[20.0, 78.0], zoom=3)
m.clear_layers()
m.add_basemap("Esri.WorldGrayCanvas")

m.add_geojson(
    geojson_data,
    layer_name="SRTM Tile Footprints",
    style={
        "color": "#d95f02",
        "weight": 1,
        "fillColor": "#d95f02",
        "fillOpacity": 0.08,
    },
    hover_style={
        "color": "#1b9e77",
        "weight": 2.5,
        "fillOpacity": 0.3,
    },
)

output_file = os.path.abspath("srtm_tile_footprints.html")
m.to_html(output_file)
webbrowser.open(f"file://{output_file}")
