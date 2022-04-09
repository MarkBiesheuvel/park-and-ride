#!/usr/bin/env python3
from boto3 import client
from time import time
from os import environ

if 'DATABASE_NAME' not in environ or 'TABLE_NAME' not in environ:
    exit('Environment variables not set')

database_name = environ['DATABASE_NAME']
table_name = environ['TABLE_NAME']
timestream = client('timestream-write')


def handler(locations, context):
    common_attributes = {
        'Time': str(int(time())),
        'TimeUnit': 'SECONDS'
    }

    records = [
        {
            'Dimensions': [
                {
                    'Name': 'Location',
                    'Value': location['Location'],
                    'DimensionValueType': 'VARCHAR',
                }
            ],
            'MeasureName': 'Availability',
            'MeasureValue': str(location['Availability']),
            'MeasureValueType': 'BIGINT',
        }
        for location in locations
    ]

    timestream.write_records(
        DatabaseName=database_name,
        TableName=table_name,
        CommonAttributes=common_attributes,
        Records=records,
    )
