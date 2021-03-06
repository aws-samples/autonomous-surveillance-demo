#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
#
cmake_minimum_required(VERSION 2.8.3)
project(aws_iot_connector)

find_package(catkin REQUIRED COMPONENTS
  move_base_msgs
  rospy
  std_msgs
  nav_msgs
  message_generation
)

catkin_package()

#############
## Install ##
#############

catkin_install_python(PROGRAMS
  nodes/aws_iot_connector.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

install(DIRECTORY launch/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch)
install(DIRECTORY certs/ DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/certs)
