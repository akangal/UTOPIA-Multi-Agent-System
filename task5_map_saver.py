#!/usr/bin/env python

import rospy
from sensor_msgs.msg import PointCloud2
import pcl
import rospkg
import numpy as np
from sensor_msgs import point_cloud2

def save_point_cloud(msg):
    # Convert PointCloud2 message to pcl.PointCloud
    pc_data = list(point_cloud2.read_points(msg))
    cloud_np = np.array(pc_data, dtype=np.float32)

    # Create a list of tuples containing XYZ coordinates
    points_list = [(x, y, z) for x, y, z, _ in cloud_np]

    # Create a new PCL point cloud
    cloud = pcl.PointCloud(points_list)

    # Get the path to the 'utopia_real' package's 'map' folder
    rospack = rospkg.RosPack()
    utopia_real_path = rospack.get_path('utopia_real')
    map_folder_path = utopia_real_path + '/maps/'

    # Save the point cloud in PCD format under the 'map' folder
    pcl.save(cloud, map_folder_path + 'Task5_map.pcd')
    rospy.loginfo('Task5 map saved as Task5_map.pcd under utopia_real package map folder')

def main():
    rospy.init_node('agv_map_saver_node', anonymous=True)

    # Subscribe to the fused point cloud topic from ZED Mini mapping
    rospy.Subscriber('/zedm/zed_node/mapping/fused_cloud', PointCloud2, save_point_cloud)

    # Keep the node running until manually stopped
    rospy.spin()

if __name__ == '__main__':
    main()

