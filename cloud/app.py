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

from aws_cdk import core

from dynamo.resource import DynamoResource
from greengrass.resource import GreengrassResource
from stream_processor.resource import StreamProcessorResource
from webrtc.resource import KinesisVideoWebRTCResource


class DemoStack(core.Stack):
    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        stream_processor = StreamProcessorResource(
            self, "KinesisVideoResource",
        )

        core.CfnOutput(
            self, "S3Bucket",
            description="The name of S3 Bucket to upload pictures for the collection",
            value=stream_processor.bucket_name,
        )
        core.CfnOutput(
            self, "CollectionID",
            description="The name of the collection",
            value=stream_processor.collection_id,
        )

        DynamoResource(self, "DynamoResource", kinesis_stream=stream_processor.stream)
        KinesisVideoWebRTCResource(self, "KinesisVideoWebRTCResource")
        greengrass = GreengrassResource(self, "GreengrassResource")

        core.CfnOutput(
            self, "GreengrassSystemdLambda",
            description="The name of lambda function for Greengrass group",
            value=greengrass.systemd_lambda.function_name,
        )


app = core.App()
DemoStack(app, "AutonomousSurveillanceDemoStack")
app.synth()
