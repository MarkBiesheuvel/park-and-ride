#!/usr/bin/env python3
import os
from constructs import Construct
from aws_cdk import (
    App,
    Environment,
    Stack,
    Duration,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_lambda_destinations as destinations,
    aws_timestream  as timestream,
)

class ParkAndRideStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = timestream.CfnDatabase(self, 'Database')

        table = timestream.CfnTable(self, 'Table',
            database_name=database.ref,
            retention_properties={
                'MemoryStoreRetentionPeriodInHours': 48, # 2 days
                'MagneticStoreRetentionPeriodInDays': 365, # 1 year
            },
        )

        store_function = lambda_.Function(
            self, 'StoreFunction',
            description='Stores data in database',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/store/'),
            timeout=Duration.seconds(10),
            handler='index.handler',
            environment={
                'DATABASE_NAME': database.ref,
                'TABLE_NAME': table.attr_name,
            },
        )

        store_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:DescribeEndpoints'],
                resources=['*'],
            )
        )

        store_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:WriteRecords'],
                resources=[table.attr_arn],
            )
        )

        fetch_function = lambda_.Function(
            self, 'FetchFunction',
            description='Fetches data from source',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/fetch/'),
            timeout=Duration.seconds(10),
            handler='index.handler',
            on_success=destinations.LambdaDestination(
                fn=store_function,
                response_only=True,
            )
        )

        rule = events.Rule(self, "Rule",
            schedule=events.Schedule.cron(minute='*/5'),  # Every 5 minutes
            targets=[
                targets.LambdaFunction(
                    handler=fetch_function,
                    retry_attempts=3,
                    max_event_age=Duration.minutes(5),
                    event=events.RuleTargetInput.from_object({
                        'url': 'https://penr.stachanov.com/penr/currentAvailability/'
                    }),
                )
            ],
        )

        api_function = lambda_.Function(self, 'Api',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler='index.handler',
            code=lambda_.Code.from_asset('./src/api'),
            environment={
                'DATABASE_NAME': database.ref,
                'TABLE_NAME': table.attr_name,
            },
        )
        api_function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE
        )
        api_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:Select'],
                resources=[table.attr_arn],
            )
        )
        api_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=['timestream:DescribeEndpoints'],
                resources=['*'],
            )
        )


app = App()
ParkAndRideStack(app, 'ParkAndRide',
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)
app.synth()
