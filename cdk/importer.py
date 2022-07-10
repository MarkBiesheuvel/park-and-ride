#!/usr/bin/env python3
from constructs import Construct
from datastore import Datastore
from aws_cdk import (
    Duration,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_lambda_destinations as destinations,
)

class Importer(Construct):

    def __init__(self, scope: Construct, id: str, datastore: Datastore, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        store_function = lambda_.Function(
            self, 'StoreFunction',
            description='Stores data in database',
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset('src/store/'),
            timeout=Duration.seconds(10),
            handler='index.handler',
            environment={
                'DATABASE_NAME': datastore.database_name,
                'TABLE_NAME': datastore.table_name,
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
                resources=[datastore.table_arn],
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

        rule = events.Rule(self, "ImportRule",
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