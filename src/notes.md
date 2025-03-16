# Steps

0. Activate ```source soilenv/bin/activate```
1. Run ```soil_pystac.py``` to download data from Microsoft Planetary Computer
2. Data will download to a directory called ```soil_rasters```
3. Run ```merge_soil_channels.py``` to merge the soil channels into a single raster
4. Final data will be saved as ```soil.nc``` in the directory ```soil_rasters```