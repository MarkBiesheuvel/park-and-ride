#!/usr/bin/env python3
from constructs import Construct
from datastore import Datastore
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
)

class Api(Construct):

    def __init__(self, scope: Construct, id: str, datastore: Datastore, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        api_function = lambda_.Function(self, 'Api',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler='index.handler',
            code=lambda_.Code.from_asset('./src/api'),
            environment={
                'DATABASE_NAME': datastore.database_name,
                'TABLE_NAME':  datastore.table_name,
            },
        )
        api_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE
        )
        api_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:Select'],
                resources=[datastore.table_arn],
            )
        )
        api_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:DescribeEndpoints'],
                resources=['*'],
            )
        )