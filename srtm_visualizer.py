import glob
import os
import webbrowser
import leafmap
from localtileserver import TileClient

@property
def _fixed_server_base_url(self):
    host = f"[{self.server_host}]" if ":" in self.server_host and not self.server_host.startswith("[") else self.server_host
    return f"http://{host}:{self.server_port}"

TileClient.server_base_url = _fixed_server_base_url

# Find the 2 actual .tif files inside the SRTM_GL1_srtm folder
tif_files = glob.glob(r"D:\code\terrainexploration\SRTM_GL1_srtm\*.tif")
print("Found TIF files:", tif_files)

m = leafmap.Map()
m.clear_layers()
m.add_basemap("Esri.WorldGrayCanvas")

clients = []
for tif in tif_files:
    name = os.path.basename(tif)
    client = TileClient(tif, host="127.0.0.1")
    clients.append(client)
    m.add_raster(client, layer_name=f"Elevation: {name}", colormap="terrain")

# Center map on the first available tile
if clients:
    m.center = clients[0].center()
    m.zoom = 8

output_file = os.path.abspath("srtm_map.html")
m.to_html(output_file)
webbrowser.open(f"file://{output_file}")

input("Map opened in browser. Press Enter to stop the tile server and exit...")
