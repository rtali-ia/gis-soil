import glob
import time
import xarray as xr
import rioxarray as rxr
from utilities import merge_soil_data, reproject_to_wgs84, resample_to_new_resolution

#First merge the soil data tif files that contains different geographies
if __name__ == "__main__":
    
        output_dir = "./soil_final"
    
        #Print current time in CST
        print("Current time:", time.ctime())
    
        band_names = ['nccpi3all', 'nccpi3corn', 'nccpi3soy','soc0_150', 'soc0_999', 'rootznaws', 'pctearthmc']
        
        print("Total number of bands to merge:", len(band_names))
        
        
        # for band in band_names:
        #     start_time = time.time()
        #     try:
        #         merge_soil_data("soil_rasters", output_dir, band)
        #     except Exception as e:
        #         print(f"Error: {e}")
        #         continue
            
        #     print(f"Total time taken for Merging {band}: {time.time() - start_time} seconds.")
        
        
        #Reproject merged files to WGS84
        # for band in band_names:
        #     start_time = time.time()
        #     try:
        #         input_path = f"{output_dir}/merged_max_{band}.tif"
        #         output_path = f"{output_dir}/merged_max_{band}_wgs84.tif"
        #         reproject_to_wgs84(input_path, output_path, src_crs='ESRI:102039', dst_crs='EPSG:4326')
        #     except Exception as e:
        #         print(f"Error: {e}")
        #         continue

        #     print(f"Total time taken for Reprojection to WGS84: {time.time() - start_time} seconds.")
            
        
        
        # #Change resolution of the reprojected files
        # for band in band_names:
        #     start_time = time.time()
        #     try:
        #         input_path = f"{output_dir}/merged_max_{band}_wgs84.tif"
        #         output_path = f"{output_dir}/merged_max_{band}_wgs84_resampled.tif"
        #         resample_to_new_resolution(input_path, output_path)
        #     except Exception as e:
        #         print(f"Error: {e}")
        #         continue
            
        #     print(f"Total time taken for Resampling to new resolution: {time.time() - start_time} seconds.")
        
        
        #merge all the reprojected files into a single file using xarray
        
        # Path to your TIFF files
        tif_files = sorted(glob.glob(f"{output_dir}/*_wgs84.tif"))  # Adjust the path

        # Load all TIFFs into a list of xarray DataArrays
        bands = [rxr.open_rasterio(f).squeeze() for f in tif_files]

        # Stack along a new "band" dimension
        stacked = xr.concat(bands, dim="band")

        # Save to NetCDF
        encoding = {"band": {"zlib": True, "complevel": 5}}
        stacked.to_netcdf(f"./{output_dir}/soil.nc", engine="netcdf4", encoding=encoding)

        print("NetCDF file saved as soil.nc")
    
   
    
    
    
    