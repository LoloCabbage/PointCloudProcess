

# ## Get the lowest points


import numpy as np
import laspy

def read_laz_file(file_path):
    las = laspy.read(file_path)
    points = np.vstack((las.x, las.y, las.z)).transpose()
    return points

def create_grid_and_find_lowest_points(points, grid_size):
    
    # These two lines calculate the minimum and maximum x and y coordinates among all points. 
    # This is used to determine the extent of the grid.
    min_x, min_y, _ = np.min(points, axis=0)
    max_x, max_y, _ = np.max(points, axis=0)
    print("min_x, min_y: ", min_x, min_y)
    print("max_x, max_y: ", max_x, max_y)
    
    # Create grid
    # These two lines create a sequence of x and y coordinates that represent the positions of the grid lines, 
    # plus grid_size for later use. grid_size is the size of the grid cells.
    x_coords = np.arange(min_x, max_x, grid_size)
    y_coords = np.arange(min_y, max_y, grid_size)

    lowest_points = []
    for x in x_coords:
        for y in y_coords:
            # Find the point in the grid
            in_grid = (points[:, 0] >= x) & (points[:, 0] < x + grid_size) & \
                      (points[:, 1] >= y) & (points[:, 1] < y + grid_size)
            grid_points = points[in_grid]

            if len(grid_points) > 0:
                # Select the point with the smallest z value
                lowest_point = grid_points[np.argmin(grid_points[:, 2])]
                lowest_points.append(lowest_point)
            else:
                # Print the position of the grid without data
                print(f"No data in grid at position: x={x}, y={y}")

    return np.array(lowest_points)

grid_size = 40  # Maximum building 33x33m
input_laz_path = "600_thinned_025_filtered.laz"
points=read_laz_file(input_laz_path)
lowest_points = create_grid_and_find_lowest_points(points, grid_size)

print(len(lowest_points)) #If =225, there is no cell with no data


# ## Form the original TIN by lowest points and find other ground points


import matplotlib.pyplot as plt
import startinpy
from tqdm import tqdm

class Tin:
    def __init__(self):
        self.dt = startinpy.DT()
        
    def insert_lowest_pts(self,arr): # insert a lot of point at the same time and create TIN
        return self.dt.insert(arr)

    def number_of_vertices(self):
        return self.dt.number_of_vertices()

    def number_of_triangles(self):
        return self.dt.number_of_triangles()

    def insert_ground_pt(self, point): # insert a point
        x=point[0]
        y=point[1]
        z=point[2]
        return self.dt.insert_one_pt(x, y, z)
    
    def insert_one_pt(self, x, y, z):
        self.dt.insert_one_pt(x, y, z)


    def info(self):
        print(self.dt.points)

    def get_delaunay_vertices(self):
        return self.dt.points
    
    def get_triangles(self):
        return self.dt.triangles
    
    
    def get_location(self,point): # get the point is located in which triangle 
        x=point[0]
        y=point[1]
        return self.dt.locate(x,y)
    
    
        """    
    def get_all_triangle_index(self):
        pts = self.dt.points
        edges = []
        for tr in self.dt.triangles:
            
            a = tr            
            edges.append(a)

        return edges
        
        """

    def get_p123(self,arr): # get the coordinate from the index
        pts=self.dt.points
        p123=[]
        

        a=pts[arr[0]]
        b=pts[arr[1]]
        c=pts[arr[2]]

        p123.append(a)
        p123.append(b)
        p123.append(c)
            
        return p123
    
    def is_inside_tin(self,point): 
        # check the point is inside the tin or not 
        # convex hull is formed by the lowest points
        
        x=point[0]
        y=point[1]
        
        return self.dt.is_inside_convex_hull(x,y)

    def find_distance_and_add_points(self, points): # main function 
        results = []

        for point in tqdm(points, desc="Processing points"):
            
            inside_index = self.is_inside_tin(point)
    
            if not inside_index:
                results.append((point, None, None, False))  # not inside TIN
                continue

            arr = self.get_location(point)
            p123 = self.get_p123(arr)
            p1, p2, p3 = p123[0], p123[1], p123[2]
            
            # Calculate distance
            normal_vector = np.cross(p2 - p1, p3 - p1)
            normal_vector /= np.linalg.norm(normal_vector)
            a, b, c = normal_vector
            d = -np.dot(normal_vector, p1)
            distance = abs(a * point[0] + b * point[1] + c * point[2] + d) / np.linalg.norm(normal_vector)

            # Calculate alpha
            vectors = [point - p1, point - p2, point - p3]
            max_angle = 0

            for v in vectors:
                norm_v = np.linalg.norm(v)
                if norm_v == 0:
                    # print("the same point")
                    continue

                v /= norm_v
                cos_angle = np.dot(v, normal_vector)
                angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
                complement_angle = np.pi / 2 - angle
                max_angle = max(max_angle, complement_angle)

            alpha = np.degrees(max_angle)

            # Determine whether to add points
            if distance < 0.15651385846605634 and alpha < 1.4878249952648377:  
                # this is the threshold from 0.1 thining
                # will be change in the following
                self.insert_ground_pt(point)
                results.append((point, distance, alpha, True))
            else:
                results.append((point, distance, alpha, False))

        return results


# ## Build the TIN and use it



initial_points=lowest_points

tin = Tin()
tin.insert_lowest_pts(initial_points)
print(tin.number_of_vertices())
print(tin.number_of_triangles())



query_points = points
results = tin.find_distance_and_add_points(query_points)



# ## Save data to laz files



import numpy as np
import laspy

data = results

filtered_points = [item[0] for item in data if item[-1]]

header = laspy.LasHeader(version="1.2", point_format=1)
outfile = laspy.LasData(header)

if filtered_points:
    all_points = np.array(filtered_points)
    outfile.x = all_points[:, 0]
    outfile.y = all_points[:, 1]
    outfile.z = all_points[:, 2]

    outfile.write("600_GP_output.laz")
else:
    print("No points with the last attribute as True.")





