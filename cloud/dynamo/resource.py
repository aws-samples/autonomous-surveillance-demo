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

from aws_cdk import (
    core,
    aws_lambda,
)
from aws_cdk.aws_dynamodb import Table, BillingMode, Attribute, AttributeType, StreamViewType
from aws_cdk.aws_iam import ManagedPolicy
from aws_cdk.aws_lambda import Function, StartingPosition
from aws_cdk.aws_lambda_event_sources import KinesisEventSource, DynamoEventSource

class DynamoResource(core.Construct):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.table = self.create_table()
        table_name = self.table.table_name
        self.consumer = self.create_consumer_function(table_name, kwargs["kinesis_stream"])
        self.publisher = self.create_publisher_function(table_name)

    def create_table(self):
        table = Table(
            self, "RekognitionResult",
            partition_key=Attribute(name="camera", type=AttributeType.STRING),
            sort_key=Attribute(name="timestamp", type=AttributeType.NUMBER),
            time_to_live_attribute="expire",
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_IMAGE
        )
        return table

    def create_consumer_function(self, table_name, stream):
        with open("dynamo/consumer.py", encoding="utf-8") as fp:
            code_body = fp.read()

        code_body.replace(":TableName:", table_name)

        lambda_function = Function(
            self, "ConsumerFunction",
            code=aws_lambda.InlineCode(code_body),
            handler="index.main",
            timeout=core.Duration.seconds(3),
            runtime=aws_lambda.Runtime.PYTHON_3_7,
        )
        lambda_function.role.add_managed_policy(ManagedPolicy.from_managed_policy_arn(
            self, "AWSLambdaKinesisExecutionRole",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole"
        ))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"))
        lambda_function.add_event_source(KinesisEventSource(
            stream,
            batch_size=10,
            starting_position=StartingPosition.LATEST,
        ))
        return lambda_function

    def create_publisher_function(self, table_name):
        with open("dynamo/publisher.py", encoding="utf-8") as fp:
            code_body = fp.read()

        code_body.replace(":TableName:", table_name)

        lambda_function = Function(
            self, "PublisherFunction",
            code=aws_lambda.InlineCode(code_body),
            handler="index.main",
            timeout=core.Duration.seconds(3),
            runtime=aws_lambda.Runtime.PYTHON_3_7,
        )
        lambda_function.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBReadOnlyAccess"))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AWSIoTDataAccess"))
        lambda_function.add_event_source(DynamoEventSource(
            self.table,
            starting_position=StartingPosition.TRIM_HORIZON,
            batch_size=5,
        ))
        return lambda_function
