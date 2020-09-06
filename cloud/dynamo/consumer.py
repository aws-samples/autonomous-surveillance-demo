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

import base64
import json
import logging

import boto3

# prepare for logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# rekognition　threshold
CONFIDENCE_THRESHOLD = 80


def find_name(face):
    """ return name for recognized person """
    if not face["MatchedFaces"]:
        return ""
    confidence = face["MatchedFaces"][0]["Similarity"]
    if confidence < CONFIDENCE_THRESHOLD:
        return ""
    return face["MatchedFaces"][0]["Face"]["ExternalImageId"]


def main(event, context):
    logger.info(f"Received event: {json.dumps(event, indent=2)}")

    # set up DynamoDB resource using boto3
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table(':TableName:')

    for record in event['Records']:
        # get data out of kinesis data streams and put them in variables
        event_source = record["eventSourceARN"].split("/")[-1]
        payload = json.loads(base64.b64decode(record['kinesis']['data']))
        logger.info(f"Decoded payload: {payload}")
        timestamp = payload["InputInformation"]["KinesisVideo"]["ServerTimestamp"]
        names = [find_name(face) for face in payload["FaceSearchResponse"]]
        num_unknown = names.count("")
        names = [name for name in names if name != ""]
        logger.info(f'stream: {event_source}, unknown={num_unknown}, names={names}')

        # put Item into DynamoDB
        timestamp = int(timestamp)
        expire = timestamp + 10
        table.put_item(
            Item={
                'camera': event_source,
                'timestamp': timestamp,
                'unknown': num_unknown,
                'expire': expire
            }
        )

    return {"result", "ok"}
