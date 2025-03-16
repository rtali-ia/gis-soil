"""
Check the CRS of the input data
"""

import xarray as xr
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling


def check_crs(file_path):
    """
    Check the CRS of the input data
    """
    
    with rasterio.open(file_path) as src:
        print("CRS:", src.crs)

if __name__ == "__main__":
    # Path to the input file
    file_path = "/work/mech-ai-scratch/rtali/gis-soil/soil_final/merged_max_nccpi3all.tif"
    
    # Check the CRS of the input data
    check_crs(file_path)
    
    # Plot the preview image
    with rasterio.open(file_path) as src:
        show(src)
        plt.savefig("preview.png")
    
    print("CRS checked successfully!")