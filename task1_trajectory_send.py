#!/usr/bin/env python

import rospy
import os
import shutil
import rospkg
from subprocess import Popen
from std_msgs.msg import String
import time  # Import the time module

# Get the list of active ROS nodes
nodes = rospy.get_published_topics()

# Initialize the simulation variable as True
simulation = True
tracking_package = "tracking_pid"
tracking_launch="tracking.launch"
robot_name="droneID:=quad1"

# Check if any topic contains 'gazebo' in its name. If gazebo runs, that means it is a simulation environment
simulation = any('/gazebo' in topic for topic, _ in nodes)
if simulation:
    tracking_package = "tracking_pid"
    tracking_launch="tracking.launch"
    robot_name="droneID:=quad1"
else:
    tracking_package = "utopia_real"
    tracking_launch="send_trajectory.launch"
    robot_name="droneID:=ryobi1"

class TrajectoryLoaderNode:
    def __init__(self):
        rospy.init_node('task1_trajectory_sender_node')

        # Set the destination folder in the tracking_pid package
        self.pkg_path = rospkg.RosPack().get_path('tracking_pid')
        self.destination_folder = os.path.join(self.pkg_path, 'trajectories')

        # Subscribe to the task1_status topic
        self.task_status_sub = rospy.Subscriber("/task1_status", String, self.task_status_callback)

        # Initialize a flag to check if the trajectory is generated
        self.trajectory_generated = False

    def task_status_callback(self, msg):
        if msg.data == "Trajectory is generated.":
            self.trajectory_generated = True
            time.sleep(10)  # Sleep for 10 seconds while the previous nodes are being killed.
            self.load_trajectory()

    def load_trajectory(self):
        try:
            # Get the trajectory parameter after it is generated
            self.trajectory_param = rospy.get_param("task1/trajectory")

            # Copy the trajectory file to the destination folder
            shutil.copy(self.trajectory_param, os.path.join(self.destination_folder, os.path.basename(self.trajectory_param)))

            # Wait for the Enter key press
            input("Press Enter to launch the trajectory...")

            # Launch tracking.launch with appropriate parameters
            launch_command = [
                "roslaunch",
                tracking_package,
                tracking_launch,
                f"trajectory:={os.path.splitext(os.path.basename(self.trajectory_param))[0]}",  # Set trajectory parameter without extension
                robot_name  # Set the droneID parameter
            ]

            # Run the launch command
            Popen(launch_command)

        except Exception as e:
            rospy.logerr(f"Error loading trajectory: {str(e)}")

if __name__ == '__main__':
    try:
        node = TrajectoryLoaderNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

