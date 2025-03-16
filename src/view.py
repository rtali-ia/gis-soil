#View tif files
import os
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
import glob

if __name__ == "__main__":
    # List all the files in the directory
    preview_files = glob.glob("./soil_rasters/*_preview.tif")
    
    # Plot the preview images one by one
    for file in preview_files:
        try:
            with rasterio.open(file) as src:
                show(src)
                #Extract the filename without the extension and the path
                file_name = os.path.splitext(os.path.basename(file))[0]
                print(f"Plotting {file_name}")
                #Save the plot as a png file
                plt.savefig(f"./plots/{file_name}.png")
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue
            
            