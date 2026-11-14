import rasterio  # Must be imported first to initialize GDAL properly
import webbrowser
import os
import leafmap
from localtileserver import TileClient

@property
def _fixed_server_base_url(self):
    host = f"[{self.server_host}]" if ":" in self.server_host and not self.server_host.startswith("[") else self.server_host
    return f"http://{host}:{self.server_port}"

TileClient.server_base_url = _fixed_server_base_url

vrt_path = os.path.abspath(r"D:\code\terrainexploration\SRTM_GL1_srtm.vrt")
import rasterio

with rasterio.open(vrt_path) as src:
    print("Files referenced by VRT:", src.files[:5])
    # Try reading a tiny 10x10 pixel window from the top-left corner
    data = src.read(1, window=((0, 10), (0, 10)))
    print("Read success! Shape:", data.shape)

client = TileClient(vrt_path, host="127.0.0.1")
m = leafmap.Map()
m.add_basemap("Esri.WorldGrayCanvas")
m.center = [12.97, 77.59]
m.zoom = 10
m.add_raster(client, layer_name="VRT Layer")

# Save the map to an HTML file and launch it in your default browser
output_file = os.path.abspath("srtm_map.html")
m.to_html(output_file)
webbrowser.open(f"file://{output_file}")

# Keep the script alive so the local tile server stays running while you view the map
input("Map opened in browser. Press Enter in this terminal to stop the tile server and exit...")


