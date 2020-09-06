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
import os

from aws_cdk import (
    aws_cloudformation as cfn,
    aws_lambda as lambda_,
    core
)
from aws_cdk.aws_iam import ManagedPolicy, Role, ServicePrincipal, PolicyStatement, PolicyDocument


class KinesisVideoWebRTCResource(core.Construct):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)
        self.account = os.environ["CDK_DEFAULT_ACCOUNT"]
        self.region = os.environ["CDK_DEFAULT_REGION"]

        policy_name = "AutonomousSurveillanceKVSPolicy"
        role_name = "AutonomousSurveillanceIoTRole"
        role = self.create_role(role_name, policy_name)
        kwargs["RoleARN"] = role.role_arn

        role_alias_name = "AutonomousSurveillanceRoleAlias"
        iot_policy_name = "AutonomousSurveillanceKVSPolicy"
        kwargs["RoleAlias"] = role_alias_name
        kwargs["PolicyName"] = iot_policy_name
        kwargs["Region"] = self.region
        kwargs["Account"] = self.account
        self.lambda_function = self.create_lambda()
        cfn.CustomResource(
            self, "Resource",
            provider=cfn.CustomResourceProvider.lambda_(self.lambda_function),
            properties=kwargs,
        )

    def create_role(self, role_name, policy_name):

        role_statement = PolicyStatement(
            actions=["iam:GetRole", "iam:PassRole"],
            resources=[f"arn:aws:iam::{self.account}:role/{role_name}"],
        )
        kvs_statement = PolicyStatement(
            actions=[
                "kinesisvideo:DescribeSignalingChannel",
                "kinesisvideo:CreateSignalingChannel",
                "kinesisvideo:GetSignalingChannelEndpoint",
                "kinesisvideo:GetIceServerConfig",
                "kinesisvideo:ConnectAsMaster"
            ],
            resources=[f"arn:aws:kinesisvideo:{self.region}:{self.account}:channel/*/*"],
        )
        policy_document = PolicyDocument(statements=[role_statement, kvs_statement])

        role = Role(
            self, role_name,
            assumed_by=ServicePrincipal('credentials.iot.amazonaws.com'),
            role_name=role_name,
            inline_policies=[policy_document],
        )
        return role

    def create_lambda(self):
        with open("webrtc/handler.py", encoding="utf-8") as fp:
            code_body = fp.read()

        lambda_function = lambda_.SingletonFunction(
            self, "Singleton",
            uuid="5419844c-e67d-4b97-86da-7f540c8cfa4e",
            code=lambda_.InlineCode(code_body),
            handler="index.main",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.PYTHON_3_7,
        )
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AWSIoTFullAccess"))
        lambda_function.role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"))
        return lambda_function
