#!/bin/bash

source /opt/ros/melodic/setup.bash
source /home/pi/robot_ws/install/setup.bash
export ROS_HOSTNAME=$(hostname).local
export ROS_MASTER_URI=http://$ROS_HOSTNAME:11311

roslaunch autonomous_surveillance robot_navigation.launch
