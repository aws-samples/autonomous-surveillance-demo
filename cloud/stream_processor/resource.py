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
    aws_cloudformation as cfn,
    aws_lambda as lambda_,
    core
)
from aws_cdk.aws_iam import ManagedPolicy, Role, ServicePrincipal
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_kinesis import Stream


class StreamProcessorResource(core.Construct):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        s3_bucket = Bucket(self, "CollectionBucket")
        self.bucket_name = s3_bucket.bucket_name

        self.stream = Stream(self, "RekognitionStream")
        kwargs["StreamARN"] = self.stream.stream_arn

        role_name = "autonomous-surveillance-demo-stream-processor-role"
        self.role = self.create_role(role_name)
        kwargs["RoleARN"] = self.role.role_arn

        self.collection_id = "autonomous-surveillance-demo-collection"
        kwargs["CollectionID"] = self.collection_id

        self.lambda_function = self.create_lambda()

        cfn.CustomResource(
            self, "Resource",
            provider=cfn.CustomResourceProvider.lambda_(self.lambda_function),
            properties=kwargs,
        )

    def create_role(self, role_name):
        role = Role(
            self, "StreamProcessorRole",
            assumed_by=ServicePrincipal('rekognition.amazonaws.com'),
            role_name=role_name,
        )
        role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisFullAccess"))
        role.add_managed_policy(ManagedPolicy.from_managed_policy_arn(
            self, "AmazonRekognitionServiceRole",
            managed_policy_arn="arn:aws:iam::aws:policy/service-role/AmazonRekognitionServiceRole"))
        return role

    def create_lambda(self):
        with open("stream_processor/handler.py", encoding="utf-8") as fp:
            code_body = fp.read()

        lambda_function = lambda_.SingletonFunction(
            self, "Singleton",
            uuid="4a3c0f1d-cb64-4646-98fb-def9f95fbbe2",
            code=lambda_.InlineCode(code_body),
            handler="index.main",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
        )
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisFullAccess"))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisVideoStreamsFullAccess"))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonRekognitionFullAccess"))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"))
        return lambda_function
