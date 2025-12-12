#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped, TwistWithCovarianceStamped
from nav_msgs.msg import Odometry
from filterpy.kalman import KalmanFilter
import numpy as np

class EkfLocalizationNode:
    def __init__(self):
        rospy.init_node('ekf_localization_node', anonymous=False)

        # Initialize EKF
        self.ekf = KalmanFilter(dim_x=6, dim_z=6)
        self.ekf.F = np.eye(6)
        self.ekf.P *= 1e-3  # Set initial covariance

        # Set measurement matrix H
        self.ekf.H = np.eye(6)

        # Get initial state from ROS parameters
        self.init_x = rospy.get_param('/init_x', 0.0)
        self.init_y = rospy.get_param('/init_y', 0.0)
        self.init_z = rospy.get_param('/init_z', 0.0)
        self.init_Y = rospy.get_param('/init_Y', 0.0)

        # Set initial state
        self.ekf.x = np.array([self.init_x, self.init_y, self.init_z, 0.0, 0.0, self.init_Y])

        # Subscribe to measurements
        self.sub_odom = rospy.Subscriber('/zedm/zed_node/odom', Odometry, self.odom_callback, queue_size=10)
        self.sub_pose = rospy.Subscriber('/zedm/zed_node/pose_with_covariance', PoseWithCovarianceStamped, self.pose_callback, queue_size=10)
        self.sub_twist = rospy.Subscriber('/zedm/zed_node/twist_with_covariance', TwistWithCovarianceStamped, self.twist_callback, queue_size=10)

        # Publish EKF output
        self.pub_odom = rospy.Publisher('/ekf_localization/odom', Odometry, queue_size=10)

    def odom_callback(self, msg):
        # Update EKF with odometry measurement
        z = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y,
                      msg.pose.pose.position.z, msg.twist.twist.linear.x,
                      msg.twist.twist.linear.y, msg.twist.twist.linear.z])

        self.ekf.predict()
        self.ekf.update(z)
        self.publish_odom()

    def pose_callback(self, msg):
        # Update EKF with pose measurement
        z = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y,
                      msg.pose.pose.position.z, 0.0, 0.0, 0.0])  # Assuming no velocity from pose

        self.ekf.predict()
        self.ekf.update(z)
        self.publish_odom()

    def twist_callback(self, msg):
        # Update EKF with twist measurement
        z = np.array([0.0, 0.0, 0.0, msg.twist.twist.linear.x,
                      msg.twist.twist.linear.y, msg.twist.twist.linear.z])

        self.ekf.predict()
        self.ekf.update(z)
        self.publish_odom()

    def publish_odom(self):
        # Publish EKF output as Odometry message
        odom_msg = Odometry()
        odom_msg.header.stamp = rospy.Time.now()
        odom_msg.header.frame_id = 'quad1/map'
        odom_msg.child_frame_id = 'quad1/base_link'

        # Set pose and twist from EKF
        odom_msg.pose.pose.position.x = self.ekf.x[0]
        odom_msg.pose.pose.position.y = self.ekf.x[1]
        odom_msg.pose.pose.position.z = self.ekf.x[2]
        odom_msg.twist.twist.linear.x = self.ekf.x[3]
        odom_msg.twist.twist.linear.y = self.ekf.x[4]
        odom_msg.twist.twist.linear.z = self.ekf.x[5]

        # Publish Odometry message
        self.pub_odom.publish(odom_msg)

if __name__ == '__main__':
    try:
        ekf_node = EkfLocalizationNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

