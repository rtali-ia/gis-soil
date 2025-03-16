import planetary_computer
import pystac_client
import requests
import concurrent.futures
import os
from tqdm import tqdm

# Define Iowa bounding box (Modify as needed)
bbox = [-96.6395, 40.3754, -90.1401, 43.5014]  # [min lon, min lat, max lon, max lat]

# Planetary Computer STAC API URL
stac_url = "https://planetarycomputer.microsoft.com/api/stac/v1"

# Authenticate with Microsoft's Planetary Computer
client = pystac_client.Client.open(stac_url)
query = client.search(collections=["gnatsgo-rasters"], bbox=bbox)

# Fetch matching items
items = list(query.get_items())

# Create download directory
os.makedirs("soil_rasters", exist_ok=True)

# List of download tasks
download_tasks = [(item, asset_key, asset) for item in items for asset_key, asset in item.assets.items()]

def download_asset(task):
    """Download a single asset with progress tracking."""
    item, asset_key, asset = task
    signed_asset = planetary_computer.sign(asset)
    raster_url = signed_asset.href
    filename = os.path.join("soil_rasters", f"{item.id}_{asset_key}.tif")

    # Skip if file already exists
    if os.path.exists(filename):
        return filename, True

    try:
        with requests.get(raster_url, stream=True, timeout=30) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            
            with open(filename, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=f"Downloading {filename}", position=0, leave=True
            ) as pbar:
                for chunk in response.iter_content(chunk_size=65536):  # 64 KB chunk
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        return filename, False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {filename}: {e}")
        return None, False

if not download_tasks:
    print("No soil data found for the given bounding box.")
else:
    # Use ThreadPoolExecutor with high concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=35) as executor:  # Adjust to 36 cores
        results = list(tqdm(executor.map(download_asset, download_tasks), total=len(download_tasks), desc="Total Progress"))

    print("\n✅ All downloads completed.")
