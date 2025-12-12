#!/usr/bin/env python

import rospy
import os
import rospkg
from subprocess import Popen
from std_msgs.msg import String
import time

robot_name1 = "quad1"
robot_name2 = "ryobi1"
robot1_finished = False
robot2_finished = False
barcode = ""
launched = False
finished = None  # Initialize the finished variable
killed_nodes = set()  # Keep track of killed nodes
first = 0

# Wait for 5 seconds
rospy.sleep(5)
rospy.set_param('/{robot_name1}/pauseTask', False)
rospy.set_param('/{robot_name2}/pauseTask', False)
rospy.set_param('/pauseTask', False)
# Get the list of active ROS nodes
nodes = rospy.get_published_topics()

# Initialize the simulation variable as True
simulation = any('/gazebo' in topic for topic, _ in nodes)
if simulation:
    tracking_package = "tracking_pid"
    tracking_launch = "tracking.launch"
else:
    tracking_package = "utopia_real"
    tracking_launch = "send_trajectory.launch"

def check_and_kill_node(robot_name):
    global killed_nodes  # Add this line to make killed_nodes a global variable
    node_names = [
        f'{robot_name}/local_planner',
        f'{robot_name}/global_planner',
        f'{robot_name}/controller',
        f'{robot_name}/odom_converter'
    ]

    for node_name in node_names:
        if node_name not in killed_nodes:
            os.system(f'rosnode kill {node_name}')
            killed_nodes.add(node_name)
            
def barcode_callback(msg):
    global barcode, launched
    barcode = msg.data

    if barcode == 'Qubi' and launched:
        print("Robots met! Shutting down")
        os.system(f'rosnode kill /xena_just_barcode_reader')
        print("Barcode reader node is killed!")
        os.system(f'rosnode kill /find_Qubi')
        print("Find_Qubi node is killed!")
        rospy.signal_shutdown("Robots met!")

    return barcode

def traj_finished_callback(msg):
    global finished, robot1_finished, robot2_finished, barcode, launched
    finished = msg.data

    rospy.loginfo(f'Trajectory finished for robot: {finished}')
    if finished is not None and launched==False:
        check_and_kill_node(finished)

    if finished == "/quad1":
        if robot1_finished==False:
        	rospy.loginfo(f'Trajectory finished for robot: {finished}')
        robot1_finished = True
        
    if finished == "/ryobi1":
        if robot1_finished==False:
        	rospy.loginfo(f'Trajectory finished for robot: {finished}')
        robot2_finished = True

   	
    	
    if robot1_finished and robot2_finished and launched==False:
        # Launch command with appropriate parameters
        launch_cmd1 = [
            "rosrun",
            "utopia_real",
            "quad_barcode_reader_task3.py",
        ]
        Popen(launch_cmd1)
        rospy.sleep(1)

        launch_cmd2 = [
            "rosrun",
            "utopia_real",
            "find_Qubi.py",
        ]
        Popen(launch_cmd2)
        launched=True

def launch_tracking_node(robot_name, trajectory):
    global first
    if first < 2:
        package_path = rospkg.RosPack().get_path(tracking_package)
        launch_file_path = os.path.join(package_path, 'launch', tracking_launch)
        first = first + 1

        # Launch command with appropriate parameters
        launch_cmd = [
            "roslaunch",
            tracking_package,
            tracking_launch,
            f"droneID:={robot_name}",
            f"trajectory:={trajectory}"  # Added a comma here
        ]

        # Execute the launch command
        Popen(launch_cmd)

def main():
    global robot1_finished, robot2_finished
    rospy.init_node('Task3_manager')

    # Launch tracking nodes for each robot
    launch_tracking_node(robot_name2, "LfigureQubi")
    rospy.sleep(3)
    launch_tracking_node(robot_name1, "LfigureQuad")

    # Subscribe to the topic
    rospy.Subscriber("/trajFinished", String, traj_finished_callback)
    # Subscribe to the topic
    rospy.Subscriber("/xena1/barcodes", String, barcode_callback)

    # Keep the node running
    rospy.spin()

if __name__ == '__main__':
    main()

