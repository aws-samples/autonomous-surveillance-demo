# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import json
import time

import boto3
from boto3.dynamodb.conditions import Key

# set parameter for navigation
NAVIGATION_TOPIC = "autonomous-surveillance/cmd/ros"
CAMERA_POSITION = [0, 0]


def main(event, context):
    # set up DynamoDB resource using boto3
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(':TableName:')

    # set up iot client using boto3
    iot = boto3.client('iot-data')

    # check the camera
    camera = "autonomous-surveillance-demo-stream"

    # check 10 seconds backward from now
    now = int(time.time())
    for j in range(10):
        timestamp = now - j

        # query data saved j seconds before
        response = table.query(
            KeyConditionExpression=Key('camera').eq(camera) & Key('timestamp').eq(timestamp)
        )
        if not response["Items"]:
            continue

        num_unknown = response["Items"][0]["unknown"]
        # if there are unknown people, publish the location of the camera to AWS IoT so that turtlebot can automatically go there
        if num_unknown > 0:
            msg = {
                "command": "navigation",
                "action": "setGoal",
                "x": CAMERA_POSITION[0],
                "y": CAMERA_POSITION[1],
            }
            iot.publish(topic=NAVIGATION_TOPIC, qos=0, payload=json.dumps(msg))
            # publish the location of the camera to the browser
            iot.publish(topic="autonomous-surveillance/dt/telemetry", qos=0, payload=json.dumps(msg))

    return {"result", "ok"}
