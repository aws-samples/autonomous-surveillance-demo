#!/bin/bash

source /opt/ros/melodic/setup.bash
export ROS_HOSTNAME=$(hostname).local
export ROS_MASTER_URI=http://$ROS_HOSTNAME:11311

roslaunch turtlebot3_bringup turtlebot3_robot.launch
