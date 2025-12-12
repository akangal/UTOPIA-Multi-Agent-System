#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from pyzbar.pyzbar import decode
import math
from std_msgs.msg import String, Float64

def calculate_qr_orientation(polygon):
    # Assuming polygon is a list of (x, y) coordinates of the QR code's corners
    if len(polygon) == 4:
        # Calculate the vector between the first and last points
        vector_x = polygon[3][0] - polygon[0][0]
        vector_y = polygon[3][1] - polygon[0][1]

        # Calculate the angle of the vector in radians
        angle_radians = math.atan2(vector_y, vector_x)

        # Convert the angle to degrees
        angle_degrees = math.degrees(angle_radians)

        return angle_degrees

    return None

def image_callback(msg):
    try:
        cv_image = CvBridge().imgmsg_to_cv2(msg, "bgr8")

        # Barcode scanning using ZBar
        barcodes = decode(cv_image)
        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                rospy.loginfo("Found barcode: %s", barcode_data)
                rospy.loginfo("Type: %s", barcode.type)
                rospy.loginfo("Bounding box: %s", barcode.polygon)

                # Calculate and publish the orientation angle
                orientation_angle = calculate_qr_orientation(barcode.polygon)
                if orientation_angle is not None:
                    rospy.loginfo("Orientation Angle: %s degrees", orientation_angle)
                    
                    # Publish barcode data and orientation angle
                    barcode_publisher.publish(barcode_data)
                    angle_publisher.publish(orientation_angle)
                else:
                    rospy.logwarn("Cannot determine orientation. Polygon has %s points.", len(barcode.polygon))

            # Your additional image processing logic goes here

        # For example, display the image using OpenCV
        cv2.imshow("Image from /usb_cam/image_raw", cv_image) #It can be commented with #
        cv2.waitKey(1)
    except Exception as e:
        rospy.logerr("Error processing image: %s", str(e))

if __name__ == "__main__":
    rospy.init_node("xena_barcode_reader", anonymous=False)

    # Publishers
    barcode_publisher = rospy.Publisher("/xena1/barcodes", String, queue_size=10)
    angle_publisher = rospy.Publisher("/xena1/barcode_angle", Float64, queue_size=10)

    # Subscriber
    rospy.Subscriber("/usb_cam/image_raw", Image, image_callback) #/zedm/zed_node/rgb/image_rect_gray is better. /// first was: /zedm/zed_node/rgb/image_rect_color

    rospy.spin()

