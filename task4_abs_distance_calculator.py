#!/usr/bin/env python

import rospy
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool, Float64
import math
import os
import rospkg
from subprocess import Popen
import time

quad1_odometry = None
ryobi1_odometry = None

pause_param =''
pause_topic=''

# Get the list of active ROS nodes
nodes = rospy.get_published_topics()

# Global variable to track the time when radius first exceeded the limit
exceed_time_start = None


# Initialize the simulation variable as True
simulation = any('/gazebo' in topic for topic, _ in nodes)
if simulation:
    pause_param = '/quad1/pauseTask'
    pause_topic = '/quad1/pauseTask'
else:
    pause_param = '/ryobi1/pauseTask'
    pause_topic = '/ryobi1/pauseTask'



def odometry_callback_quad1(msg):
    global quad1_odometry
    quad1_odometry = msg

def odometry_callback_ryobi1(msg):
    global ryobi1_odometry
    ryobi1_odometry = msg

def calculate_radius(dif_x, dif_y):
    return math.sqrt(dif_x**2 + dif_y**2)

def check_and_set_pausetask(radius, limit_distance):
    global exceed_time_start

    current_time = time.time()

    if radius > limit_distance:
        if exceed_time_start is None:
            # Start the timer when radius exceeds the limit for the first time
            exceed_time_start = current_time
        elif current_time - exceed_time_start > 0.5:
            # If the condition has been true for more than 0.5 seconds
            rospy.set_param(pause_param, True)
            rospy.loginfo("Pausing task due to exceeding distance limit for over 0.5 seconds.")
    else:
        # If the radius does not exceed the limit or the condition hasn't been true for 0.5 seconds
        if exceed_time_start is not None:
            exceed_time_start = None  # Reset the timer
            rospy.set_param(pause_param, False)
            rospy.loginfo("Resuming task as distance is within limits.")


def main():
    global quad1_odometry, ryobi1_odometry
    
    rospy.init_node('Task4_abs_distance_calculator')

    # Parameters
    limit_distance = rospy.get_param('/limited_distance', default=3.0)

    # Subscribers
    rospy.Subscriber('quad1/odometry/abs', Odometry, odometry_callback_quad1)
    rospy.Subscriber('ryobi1/odometry/abs', Odometry, odometry_callback_ryobi1)

    # Publishers
    pausetask_publisher = rospy.Publisher(pause_topic, Bool, queue_size=10)
    abs_distance_publisher = rospy.Publisher('/abs_distance', Float64, queue_size=10)

    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        if quad1_odometry is not None and ryobi1_odometry is not None:
            dif_x = quad1_odometry.pose.pose.position.x - ryobi1_odometry.pose.pose.position.x
            dif_y = quad1_odometry.pose.pose.position.y - ryobi1_odometry.pose.pose.position.y
            rospy.loginfo(f"Computed differences - dif_x: {dif_x}, dif_y: {dif_y}")

            radius = calculate_radius(dif_x, dif_y)
            limit_distance = rospy.get_param('/limited_distance', default=3.0)

            check_and_set_pausetask(radius, limit_distance)

            # Publish the result
            pausetask_publisher.publish(rospy.get_param(pause_param, default=False))
            abs_distance_publisher.publish(radius)

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

