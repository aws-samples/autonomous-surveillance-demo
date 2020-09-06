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

import logging

import boto3

kvs = boto3.client("kinesisvideo")
reko = boto3.client("rekognition")


def create_kvs_stream(stream_name):
    res = kvs.create_stream(
        StreamName=stream_name,
        DataRetentionInHours=24,
    )
    return res["StreamARN"]


def delete_kvs_stream(stream_name):
    res = kvs.describe_stream(
        StreamName=stream_name,
    )
    kvs.delete_stream(StreamARN=res["StreamInfo"]["StreamARN"])


def create_stream_processor(processor_name, video_stream_arn, data_stream_arn, collection_id, role_arn):
    reko.create_stream_processor(
        Input={"KinesisVideoStream": {"Arn": video_stream_arn}},
        Output={"KinesisDataStream": {"Arn": data_stream_arn}},
        Name=processor_name,
        Settings={
            "FaceSearch": {
                "CollectionId": collection_id,
                "FaceMatchThreshold": 50.0,
            }
        },
        RoleArn=role_arn,
    )


def main(event, context):
    import cfnresponse

    physical_id = 'KinesisVideoResource'
    logging.getLogger().setLevel(logging.DEBUG)

    try:
        logging.info('Input event: %s', event)

        if event['RequestType'] == 'Create' and event['ResourceProperties'].get('FailCreate', False):
            raise RuntimeError('Create failure requested')

        collection_id = event['ResourceProperties']['CollectionID']
        role_arn = event['ResourceProperties']['RoleARN']
        data_stream_arn = event['ResourceProperties']['StreamARN']
        stream_name = f"autonomous-surveillance-demo-stream"
        processor_name = f"autonomous-surveillance-demo-processor"

        if event['RequestType'] == 'Create':
            reko.create_collection(CollectionId=collection_id)

            video_stream_arn = create_kvs_stream(stream_name=stream_name)
            create_stream_processor(
                processor_name=processor_name,
                video_stream_arn=video_stream_arn, data_stream_arn=data_stream_arn,
                collection_id=collection_id, role_arn=role_arn
            )
            reko.start_stream_processor(Name=processor_name)

        elif event['RequestType'] == 'Delete':
            reko.stop_stream_processor(Name=processor_name)
            reko.delete_stream_processor(Name=processor_name)
            delete_kvs_stream(stream_name=stream_name)
            reko.delete_collection(CollectionId=collection_id)

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, physical_id)

    except Exception as e:
        logging.exception(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
