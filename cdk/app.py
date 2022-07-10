#!/usr/bin/env python3
import os
from constructs import Construct
from datastore import Datastore
from importer import Importer
from api import Api
from website import Website
from aws_cdk import (
    App,
    Environment,
    Stack,
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

        # These resources are kept here to avoid replacing the already created database (which has data imported)
        cfn_database = timestream.CfnDatabase(self, 'Database')
        cfn_table = timestream.CfnTable(self, 'Table',
            database_name=cfn_database.ref,
            retention_properties={
                'MemoryStoreRetentionPeriodInHours': 48, # 2 days
                'MagneticStoreRetentionPeriodInDays': 365, # 1 year
            },
        )

        # TODO: move Timestream resource into Database construct
        datastore = Datastore(self, 'Datastore', cfn_database, cfn_table)

        # Ok
        importer = Importer(self, 'Importer', datastore=datastore)
        api = Api(self, 'Api', datastore=datastore)
        website = Website(self, 'Website')


app = App()
ParkAndRideStack(app, 'ParkAndRide',
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)
app.synth()
