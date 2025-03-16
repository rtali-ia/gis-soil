import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from utilities import resample_to_new_resolution

src = rasterio.open("./soil_final/merged_max_nccpi3all.tif")

# Define source and target CRS
src_crs = 'ESRI:102039'
dst_crs = 'EPSG:32632'

# Calculate transformation parameters
transform, width, height = calculate_default_transform(
    src_crs, dst_crs, src.width, src.height, *src.bounds
)

# Define output metadata
kwargs = src.meta.copy()
kwargs.update({
    'crs': dst_crs,
    'transform': transform,
    'width': width,
    'height': height
})

# Write the reprojected file
with rasterio.open('output.tif', 'w', **kwargs) as dst:
    for i in range(1, src.count + 1):  # Loop through bands
        reproject(
            source=rasterio.band(src, i),
            destination=rasterio.band(dst, i),
            src_transform=src.transform,
            src_crs=src_crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )
        
print("Conversion complete!")

#Convert the reprojected file to a new resolution
resample_to_new_resolution("output.tif", "output_resampled.tif", target_resolution=125)
print("Resampling complete!")

