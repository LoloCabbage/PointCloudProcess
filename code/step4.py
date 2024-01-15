import rasterio
import numpy as np
import laspy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN
from tqdm import tqdm


def read_point_cloud(file_path):
    point_cloud = laspy.read(file_path)
    header = point_cloud.header
    return point_cloud, header
def select_class(data, *class_code):
    """
    select points with specific class code
    the class code can be one or more
    here we select ground points and unclassified points
    """
    if len(class_code) == 1:
        return data[data.classification == class_code]
    else:
        return data[np.isin(data.classification, class_code)]
def show_point_cloud(data, decimation_factor=1):
    """
    （function for fast test, not finally used in this task）
    draw point cloud with matplotlib in 3D
    the color is based on classification
    """
    x = data.x[::decimation_factor]
    y = data.y[::decimation_factor]
    z = data.z[::decimation_factor]
    classification = data.classification
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    scatter = ax.scatter(x, y, z, c=classification, cmap='viridis', marker='.', s=1, alpha=0.5)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5)

    plt.show()
def write_point_cloud(data, file_name):
    """
    （function for fast test, not finally used in this task）
    write point cloud to las file
    """
    outfile = laspy.create(point_format = data.header.point_format,
                           file_version = data.header.version)
    outfile.points = data.points
    outfile.write(file_name)
def split_point_cloud(data,header,grid_size):
    """
    split point cloud into grids with specific grid size
    """
    x_min = header.x_min
    y_min = header.y_min
    x_max = header.x_max
    y_max = header.y_max

    x_range = np.arange(x_min, x_max, grid_size)
    y_range = np.arange(y_min, y_max, grid_size)
    size = (len(x_range), len(y_range))
    grids = []
    grid_centers = []

    # split by col and row, easier to reshape
    for y in tqdm(y_range, desc="Splitting grids in rows"):
        for x in x_range:
            grid_centers.append([x + grid_size / 2, y + grid_size / 2])
            mask = (data.x >= x) & (data.x < x + grid_size) & (data.y >= y) & (data.y < y + grid_size)
            if np.any(mask):
                grid_point = data[mask]
                grids.append(grid_point)
            else:
                grids.append(None)
    return grids, size, grid_centers
def has_veg(data):
    """
    check if the grid has vegetation
    with NDVI index
    """
    red = np.mean(data.red)
    nir = np.mean(data.nir)
    ndvi = (nir - red) / (nir + red)
    if ndvi>=0.2:
        return True
    else:
        return False
def db_scan(data, eps = 0.5, min_samples = 10):
    """
    cluster the point cloud with DBSCAN
    (inspired by GEO1001-ASSIGNMENT4)
    (just try, not used in this task)
    """
    las_array = np.vstack([data.x, data.y, data.z]).transpose()
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(las_array)
    labels = clustering.labels_
    point_labels = np.vstack([data.x, data.y, data.z, labels]).transpose()
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    return point_labels, n_clusters_
def show_cluster(data):
    """
    show the cluster result in 3D
    (additional function for DBSCAN)
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x = data[:,0]
    y = data[:,1]
    z = data[:,2]
    labels = data[:,3]

    colors = np.where(labels == -1, 'black', 'green')
    scatter = ax.scatter(x, y, z, c=colors)
    plt.colorbar(scatter)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    plt.show()
def write_raster(data, header, res):
    """
    write raster file with point cloud data
    """
    transform = rasterio.transform.from_origin(header.x_min, header.y_max, res, res)
    crs = 'EPSG:28992'
    with rasterio.open(f'../data/output/step4_{res}.tiff', 'w', driver='GTiff',
                       height=data.shape[0], width=data.shape[1],nodata=-9999,
                       count=1, dtype=data.dtype,
                       crs=crs, transform=transform) as dst:
        dst.write(data, 1)


def step4(file_path = '../data/processed/filtered.laz',res = 0.5):
    print("Step4 Starts!")
    las, header = read_point_cloud(file_path)
    # select unclassified points
    grid_veg = select_class(las, 1)
    # exclude points with only one return
    grid_veg = grid_veg[grid_veg.number_of_returns > 1]
    grids,size,grid_centers = split_point_cloud(grid_veg,header,res)
    height = []
    for grid in tqdm(grids, desc="Generating height raster"):
        if grid is not None:
            # judge if the grid has vegetation
            if has_veg(grid):
                height.append(max(grid.z))
            else: # nodata for no vegetation grids
                height.append(-9999)
        else: # nodata for empty grids(no valid points)
            height.append(-9999)

    # reshape and reorganize the height array for output
    height = np.array(height).reshape(size[0],size[1])
    height = np.flipud(height)

    write_raster(height,header,res)
    print("Step4 Finished!")

if __name__ == '__main__':
    step4()
