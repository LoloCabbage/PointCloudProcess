#!/usr/bin/env python
# coding: utf-8

# 02/Jan/2024
# 
# # thining + outlier removing
# 
# ## Thinning 
# 
# I use laspy.
# 1. Use the first method in the book, random. The reason for setting 0.1 is because I originally set it to 0.2, and then step 3 ran a little long...so I changed it to 0.1. Setting 0.1 means to keep one tenth of the points.
# 
# 
# 2. startinpy also has thining, but I was not very successful after a while. You can also give it a try.
# 
# 3. I have checked it with XiaoLuo on Cloud Compare, it looks OK. (14:00 02/Jan/2024)
# 
# ## Outlier removing
# 
# Outlier I use scipy.
# 
# Originally I used sklearn, but the teaching assistant said it was not suitable (there are public questions on discord)
# 
# 1. Use the fourth method in the book - knn distance.
# 2. Set the parameter to 3 and use the median. The reason is...I feel good
# 3. Corrected the problem why the cloudcompare is so strange when checking with Xiao Luo at 14:00 02/Jan/2024...because when I process it, I convert it to np.array and write it back to the laz file, which will lose some information. Such as color, Deviation Reflectance Amplitude PointSourceld UserData ScanAngleRank EdgeOf FlightLine ScanDirecitonFlag NumberOfReturns GpsTime Classification and so on. The program code has been modified to retain the message. I threw it into Cloud Compare myself and there should be no problem.
# 

# In[18]:


# Thining

import laspy
import numpy as np

def thin_laz_file(input_file, output_file, keep_fraction=0.1): # NOTICE HERE!! I use 0.1 
    # read LAZ file
    with laspy.open(input_file) as file:
        las = file.read()

    # get how many numbers
    total_points = las.header.point_count

    # Randomly select points to keep 
    # 11.1 thinning method 1 random
    chosen_indices = np.random.choice(total_points, int(total_points * keep_fraction), replace=False)

    # keep the points
    thinned_las = las[chosen_indices]

    # write into new file
    with laspy.open(output_file, mode="w", header=las.header) as outfile:
        outfile.write_points(thinned_las.points)

    print(f"Thinning complete. Saved to {output_file}")

# how to use the function
input_laz_path = "output_tile_4.laz"  # your file's path, this is the one which is cropped
output_laz_path = "thinned_outpu_01.laz"  # name of the output file

thin_laz_file(input_laz_path, output_laz_path)


# In[ ]:





# In[19]:


import laspy
import numpy as np
from scipy.spatial import KDTree

def remove_outliers_laz(file_path, k=3):
    # read laz 
    las = laspy.read(file_path)

    points = np.vstack((las.x, las.y, las.z)).transpose()

    # create KDTree
    tree = KDTree(points)

    # Calculate the k nearest neighbor distances for each point
    distances, _ = tree.query(points, k=k+1)  # k+1 Because the nearest point is itself
    median_distances = np.median(distances[:, 1:], axis=1)  # Calculate median distance

    # Determine threshold for outliers
    threshold = np.mean(median_distances) + 2 * np.std(median_distances)  # 1.1796426539499234 
 
    # Filter out outliers. Values greater than 1.1796426539499234 will be deleted.
    mask = median_distances < threshold

    # Create filtered LAS file to save 
    filtered_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)

    # Copy all the attributes in the original las, just the long list above
    for name in las.point_format.dimension_names:
        if name in las.point_format.dimension_names:
            data = getattr(las, name)
            setattr(filtered_las, name, data[mask])

    # Preserve scale factors and offsets
    # If you don’t do this step, its xyz will run away.
    filtered_las.header.scale = las.header.scale
    filtered_las.header.offset = las.header.offset

    # Save the processed file
    output_path = file_path.replace('.laz', '_filtered.laz')
    filtered_las.write(output_path)
    print(f"Filtered LAS file saved as: {output_path}")

# how to use
remove_outliers_laz("thinned_outpu_01.laz", k=3)


# In[ ]:





# In[ ]:





# ## Just the test. Ignore it
# 

# In[ ]:





# In[20]:


import laspy

def read_laz_properties(file_path):
    # 讀取LAZ文件
    laz_file = laspy.read(file_path)

    # 獲取所需的屬性
    properties = {
        "x":laz_file.x,
        "y":laz_file.y,
        "z":laz_file.z,
        "colors": laz_file.color if hasattr(laz_file, 'color') else 'No color data',
        "intensity": laz_file.intensity,
        "return_number": laz_file.return_number,
        "number_of_returns": laz_file.number_of_returns,
        "scan_direction_flag": laz_file.scan_direction_flag,
        "edge_of_flight_line": laz_file.edge_of_flight_line,
        "classification": laz_file.classification,
       # "scan_angle_rank": laz_file.scan_angle_rank,
        "user_data": laz_file.user_data,
        "point_source_id": laz_file.point_source_id,
        "gps_time": laz_file.gps_time,
        "amplitude": laz_file.amplitude if hasattr(laz_file, 'amplitude') else 'No amplitude data',
        "deviation": laz_file.deviation if hasattr(laz_file, 'deviation') else 'No deviation data'
    }

    return properties




# In[21]:


file_path = 'output_tile_4.laz' #cropped one
properties = read_laz_properties(file_path)
properties


# In[22]:


file_path = 'thinned_outpu_01.laz' # crop + thining one
properties = read_laz_properties(file_path)
properties


# In[23]:


file_path = 'thinned_outpu_01_filtered.laz' # crop + thining + outlier
properties = read_laz_properties(file_path)
properties


# In[ ]:




