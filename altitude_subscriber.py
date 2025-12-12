#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32

def altitude_callback(msg):
    rospy.loginfo(rospy.get_caller_id(), msg.data)

def listener():
    rospy.init_node('altitude_subscriber', anonymous=False)
    rospy.Subscriber("altitude", Int32, altitude_callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()

