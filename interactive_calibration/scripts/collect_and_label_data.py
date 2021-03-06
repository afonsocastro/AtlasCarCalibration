#!/usr/bin/env python

# ------------------------
#    IMPORT MODULES      #
# ------------------------
import argparse
import rospkg

import rospy
from visualization_msgs.msg import InteractiveMarkerControl, Marker, InteractiveMarker

from interactive_markers.interactive_marker_server import InteractiveMarkerServer
from interactive_markers.menu_handler import MenuHandler

from interactive_calibration.data_collector_and_labeler import DataCollectorAndLabeler

server = None
menu_handler = MenuHandler()


def menuFeedback(feedback):
    handle = feedback.menu_entry_id
    if handle == 1:  # collect snapshot
        print('Save collection selected')
        data_collector.saveCollection()

def initMenu():
    menu_handler.insert("Save collection", callback=menuFeedback)


def createInteractiveMarker(world_link):
    marker = InteractiveMarker()
    marker.header.frame_id = world_link
    trans = (1, 0, 1)
    marker.pose.position.x = trans[0]
    marker.pose.position.y = trans[1]
    marker.pose.position.z = trans[2]
    quat = (0, 0, 0, 1)
    marker.pose.orientation.x = quat[0]
    marker.pose.orientation.y = quat[1]
    marker.pose.orientation.z = quat[2]
    marker.pose.orientation.w = quat[3]
    marker.scale = 0.2

    marker.name = 'menu'
    marker.description = 'menu'

    # insert a box
    control = InteractiveMarkerControl()
    control.always_visible = True

    marker_box = Marker()
    marker_box.type = Marker.SPHERE
    marker_box.scale.x = marker.scale * 0.7
    marker_box.scale.y = marker.scale * 0.7
    marker_box.scale.z = marker.scale * 0.7
    marker_box.color.r = 0
    marker_box.color.g = 1
    marker_box.color.b = 0
    marker_box.color.a = 0.2

    control.markers.append(marker_box)
    marker.controls.append(control)

    marker.controls[0].interaction_mode = InteractiveMarkerControl.MOVE_3D

    control = InteractiveMarkerControl()
    control.orientation.w = 1
    control.orientation.x = 1
    control.orientation.y = 0
    control.orientation.z = 0
    control.name = "move_x"
    control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control.orientation_mode = InteractiveMarkerControl.FIXED
    marker.controls.append(control)

    control = InteractiveMarkerControl()
    control.orientation.w = 1
    control.orientation.x = 0
    control.orientation.y = 1
    control.orientation.z = 0
    control.name = "move_z"
    control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control.orientation_mode = InteractiveMarkerControl.FIXED
    marker.controls.append(control)

    control = InteractiveMarkerControl()
    control.orientation.w = 1
    control.orientation.x = 0
    control.orientation.y = 0
    control.orientation.z = 1
    control.name = "move_y"
    control.interaction_mode = InteractiveMarkerControl.MOVE_AXIS
    control.orientation_mode = InteractiveMarkerControl.FIXED
    marker.controls.append(control)

    server.insert(marker, markerFeedback)
    menu_handler.apply(server, marker.name)


def markerFeedback(feedback):
    print('Received feedback')


if __name__ == "__main__":
    # Parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--marker_scale", help='Scale of the interactive markers.', type=float, default=0.5)
    ap.add_argument('-o', '--output_folder', help='Output folder to where the collected data will be stored.', type=str,
                    required=True)
    ap.add_argument("-c", "--calibration_file", help='full path to calibration file.', type=str, required=True)
    args = vars(ap.parse_args())

    # Initialize ROS stuff
    rospy.init_node("collect_and_label")
    # rospack = rospkg.RosPack()  # get an instance of RosPack with the default search paths
    server = InteractiveMarkerServer("data_labeler")
    robot_description = rospy.get_param('/robot_description')
    rospy.sleep(0.5)

    # Process robot description and create an instance of class Sensor for each sensor
    data_collector = DataCollectorAndLabeler(args['output_folder'],
                                             server, menu_handler,
                                             args['marker_scale'], args['calibration_file'])

    createInteractiveMarker(data_collector.world_link)
    initMenu()
    menu_handler.reApply(server)
    server.applyChanges()
    print('Changes applied ...')

    rospy.spin()
