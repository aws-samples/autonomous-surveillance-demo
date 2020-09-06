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

iot = boto3.client("iot")


def main(event, context):
    import cfnresponse

    physical_id = 'IoTResource'
    logging.getLogger().setLevel(logging.DEBUG)

    try:
        logging.info('Input event: %s', event)

        if event['RequestType'] == 'Create' and event['ResourceProperties'].get('FailCreate', False):
            raise RuntimeError('Create failure requested')

        role_alias_name = event['ResourceProperties']['RoleAlias']
        role_arn = event['ResourceProperties']['RoleARN']
        policy_name = event['ResourceProperties']['PolicyName']
        region = event['ResourceProperties']['Region']
        account = event['ResourceProperties']['Account']

        if event['RequestType'] == 'Create':
            iot.create_role_alias(
                roleAlias=role_alias_name,
                roleArn=role_arn,
            )
            policy_document = f'''{{
                "Version": "2012-10-17",
                "Statement": {{
                    "Effect": "Allow",
                    "Action": "iot:AssumeRoleWithCertificate",
                    "Resource": "arn:aws:iot:{region}:{account}:rolealias/{role_alias_name}"
                }}
            }}'''
            iot.create_policy(
                policyName=policy_name,
                policyDocument=policy_document,
            )

        elif event['RequestType'] == 'Delete':
            iot.delete_policy(policyName=policy_name)
            iot.delete_role_alias(roleAlias=role_alias_name)

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, physical_id)

    except Exception as e:
        logging.exception(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
