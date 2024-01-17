import startinpy
import numpy as np
import laspy
from tqdm import tqdm
import rasterio


def read_laz_file(file_path):
    '''
        Read a laz file, return the points array and header information

        Input:
            file_path: file path of the laz file

        Output:
            points array and header information
    '''
    las = laspy.read(file_path)
    header = las.header
    points = np.vstack((las.x, las.y, las.z)).transpose()
    return points,header


def generate_grid(bbx, cell_size=0.5):
    '''
        Generate a grid with the cellsize of 50cm * 50cm based on the input points,
        return the center of each cell in the grid, as well as number of rows and columns

        Input:
            points: an array containing points with x, y, z values

        Output:
            a list containing centers of all cells [x, y], number of rows, number of columns
    '''

    # the bounding box
    min_x = bbx[0]
    max_x = bbx[1]
    min_y = bbx[2]
    max_y = bbx[3]

    num_row = int((max_y - min_y) / cell_size)
    num_column = int((max_x - min_x) / cell_size)

    cell_centers = []

    # Calculate centers of each cell
    for i in range(0, num_row):
        for j in range(0, num_column):
            cell_center_x = min_x + cell_size/2 + j * cell_size
            cell_center_y = max_y - cell_size/2 - i * cell_size
            cell_centers.append([cell_center_x,cell_center_y])

    return cell_centers, num_row, num_column


def laplace_interpolant(points, cell_centers, num_row, num_column):
    '''
        Perform Laplace interpolation method for a grid(interpolate at the center of each cell)

        Input:
            points: a list of points with x, y, z values
            cell_centers: list of center of each cell of a grid to be interpolated

        Output:
            an array containing the interpolation values for each cell
    '''

    # generate a TIN based on the input points
    dt = startinpy.DT()
    dt.insert(points)

    cell_values = []

    points_xy = [[x,y] for x,y,z in points]

    for c in tqdm(cell_centers):
        # if the cell center is on the location of one of the sample points
        if c in points_xy:
            # find the closest point(it should be that exact sample point)
            closet_point_index = dt.closest_point(c[0],c[1])
            cell_values.append(dt.get_point(closet_point_index)[2])

        else:
            # insert the center point into the TIN
            if dt.is_inside_convex_hull(c[0], c[1]):
                index_c = dt.insert_one_pt(c[0], c[1], 0.0)

                # find the adjacent vertices to the point c
                adjacent_vertices = dt.adjacent_vertices_to_vertex(index_c)

                # find incident triangles to the point c
                incident_triangles = dt.incident_triangles_to_vertex(index_c)

                weights_pvalues = []

                for index_p in adjacent_vertices:
                    coordinates_p = dt.get_point(index_p)
                    # for each adjacent vertex pi, calculate the distance between pi and c
                    distance_p_c = np.sqrt((coordinates_p[0] - c[0]) ** 2 + (coordinates_p[1] - c[1]) ** 2)

                    voronoi_centers_xp = []

                    for tr in incident_triangles:
                        if index_p in tr:
                            # calculate the circumcenter of this triangle
                            circumcenter = calculate_circumcenter(dt.get_point(tr[0]), dt.get_point(tr[1]), dt.get_point(tr[2]))
                            voronoi_centers_xp.append(circumcenter)

                    distance_voronoi_centers = np.sqrt((voronoi_centers_xp[0][0] - voronoi_centers_xp[1][0]) ** 2 + (voronoi_centers_xp[0][1] - voronoi_centers_xp[1][1]) ** 2)

                    weight_pi = distance_voronoi_centers / distance_p_c

                    weights_pvalues.append([weight_pi, coordinates_p[2]])

            sum_of_weights = sum(row[0] for row in weights_pvalues)
            products = [row[0] * row[1] for row in weights_pvalues]
            sum_of_products = sum(products)

            c_zvalue = sum_of_products / sum_of_weights

            cell_values.append(c_zvalue)

            dt.remove(index_c)

    # transform list into numpy array
    cell_values = np.array(cell_values)
    # reshape the array into the shape of num_row rows and num_column columns
    cell_values = np.reshape(cell_values,(num_row, num_column))

    return cell_values


def calculate_circumcenter(a, b, c):
    """
        Calculate the circumcenter of one given triangle

        Input:
            vertices of the triangle
            a = [xa, ya], b = [xb, yb], c = [xc, yc]

        Output:
            circumcenter coordinates of the given triangle: [ux, uy]
    """

    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d

    return [ux, uy]


def write_raster(input_data, header, output, res):
    """
        Write raster file with point cloud data and generate output result

        Input:
            input_data: data to be written into the GeoTiff
            header: laz header information
            output: output file name
            res: resolution

        Output:
            A GeoTiff file
    """
    transform = rasterio.transform.from_origin(header.x_min, header.y_max, res, res)
    crs = 'EPSG:28992'
    with rasterio.open(output, 'w',
                       driver='GTiff',
                       height=input_data.shape[0],
                       width=input_data.shape[1],
                       nodata=-9999,
                       count=1,
                       dtype=input_data.dtype,
                       crs=crs,
                       transform=transform) as dst:
        dst.write(input_data, 1)


if __name__ == '__main__':
    # set a resolution
    res = 0.5
    # bounding box: 500*500 min_x, max_x, min_y, max_y = 188415+50, 189015-50, 311750+50, 312350-50
    grid = generate_grid([188465,188965,311800,312300], res)
    # get the cell centers coordinates
    cell_center = grid[0]
    # get the number of grid rows
    grid_row = grid[1]
    # get the number of grid columns
    grid_column = grid[2]
    # read the laz data
    data_original = read_laz_file("600_GP_output_threshold.laz")
    # transform numpy array to list
    data_points = data_original[0].tolist()
    # use the data to perform Laplace interpolation
    laplace_result = laplace_interpolant(data_points, cell_center, grid_row, grid_column)
    # write the data into GeoTiff format
    write_raster(laplace_result, data_original[1], 'dtm_0.5m.tiff',res)
