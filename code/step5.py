import rasterio
import numpy as np


def read_raster(file_path):
    """
    read raster file
    """
    with rasterio.open(file_path) as raster:
        values = raster.read(1)
    return values, raster.meta

def write_raster(data,meta):
    """
    write raster file with point cloud data
    """

    with rasterio.open(f'../data/output/step5.tiff', 'w', **meta) as dst:
        dst.write(data, 1)


def step5():
    print("Step5 Starts!")
    step3, meta3 = read_raster('../data/output/dtm.tiff')
    step4, meta4 = read_raster('../data/output/step4.tiff')

    # There is nodata in step4
    # we replace it with 0
    step4 = np.nan_to_num(step4, nan=0.0)
    step5 = step4 - step3
    step5[step5 < 0] = 0

    write_raster(step5, meta4)
    print("CHM generated!")
