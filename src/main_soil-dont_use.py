import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
import os
from multiprocessing import Pool, cpu_count
from logging_helper import setup_logger

# Bounding box for Iowa
SW_LAT, SW_LON = 40.3754, -96.6395
NE_LAT, NE_LON = 43.5014, -90.1401

# Grid resolution (~1 km per step)
LAT_STEP = 0.01
LON_STEP = 0.01

# SDA API endpoint
BASE_URL = "https://SDMDataAccess.sc.egov.usda.gov/Tabular/post.rest"

# Generate latitude and longitude grids
lats = np.arange(SW_LAT, NE_LAT, LAT_STEP)
lons = np.arange(SW_LON, NE_LON, LON_STEP)

# Create directories for saving soil data
os.makedirs("./IA_soil", exist_ok=True)
os.makedirs("./logs", exist_ok=True)

# Setup logger
myLogger = setup_logger("./logs/soil.log")


def get_mukey(lat, lon):
    """Fetch MUKEYs for a given latitude and longitude."""
    wkt_polygon = f'POLYGON(({lon} {lat}, {lon+LON_STEP} {lat}, {lon+LON_STEP} {lat+LAT_STEP}, {lon} {lat+LAT_STEP}, {lon} {lat}))'
    mukey_query = f"""
    SELECT mukey
    FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('{wkt_polygon}')
    """
    payload = {"FORMAT": "JSON", "QUERY": mukey_query}
    response = requests.post(BASE_URL, data=payload)
    try:
        data = response.json()
        return [row[0] for row in data.get('Table', [])]
    except Exception:
        return []


def get_soil_properties(mukeys, lat, lon):
    """Fetch soil properties for the given MUKEYs."""
    mukeys_str = ", ".join(f"'{mukey}'" for mukey in mukeys)
    soil_query = f"""
    SELECT component.mukey, component.compname, component.comppct_r, chorizon.hzdept_r, chorizon.hzdepb_r,
           chorizon.sandtotal_r, chorizon.silttotal_r, chorizon.claytotal_r,
           chorizon.om_r, chorizon.dbthirdbar_r, chorizon.ksat_r
    FROM component
    INNER JOIN chorizon ON component.cokey = chorizon.cokey
    WHERE component.mukey IN ({mukeys_str})
    """
    payload = {"FORMAT": "JSON", "QUERY": soil_query}
    response = requests.post(BASE_URL, data=payload)
    try:
        data = response.json()
        myLogger.info(f"Received soil data for Latitude: {lat}, Longitude: {lon}")
        return [(lat, lon, *record) for record in data.get('Table', [])]
    except Exception:
        myLogger.error(f"Failed to get soil data for Latitude: {lat}, Longitude: {lon}")
        return []


def process_lon(lon, lat):
    """Process soil data retrieval for a single longitude at a given latitude."""
    mukeys = get_mukey(lat, lon)
    if mukeys:
        return get_soil_properties(mukeys, lat, lon)
    return []


def process_lat(lat):
    """Process all longitudes for a given latitude in parallel using multiprocessing."""
    with Pool(processes=30) as pool:  # Use 30 processes
        results = pool.starmap(process_lon, [(lon, lat) for lon in lons])

    # Flatten the list of results
    results = [item for sublist in results for item in sublist]

    if results:
        # Convert to DataFrame
        columns = ['latitude', 'longitude', 'mukey', 'compname', 'comppct_r' ,'hzdept_r', 'hzdepb_r',
                   'sandtotal_r', 'silttotal_r', 'claytotal_r', 'om_r', 'dbthirdbar_r', 'ksat_r']
        df = pd.DataFrame(results, columns=columns)

        # Save to CSV
        df.to_csv(f"./IA_soil/iowa_soil_properties_{lat}.csv", index=False)


if __name__ == "__main__":
    start_time = time.time()

    # Process each latitude in sequence, while parallelizing longitude processing
    for lat in tqdm(lats, desc="Processing Latitudes"):
        process_lat(lat)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    # Count the number of files saved
    total_files = len(os.listdir("./IA_soil"))
    print(f"Total number of files saved: {total_files}")
    print("Soil data saved successfully at ./IA_soil !")
