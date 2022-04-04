#!/usr/bin/env python3
from boto3 import client
from time import time
from os import environ

if 'TABLE_NAME' in environ:
    database_name, table_name = environ['TABLE_NAME'].split('|')
    timestream = client('timestream-write')
else:
    exit('Environment variable "TABLE_NAME" not set')


def handler(event, context):
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
            'MeasureValue': location['Availability'],
            'MeasureValueType': 'BIGINT',
        }
        for location in event
    ]

    timestream.write_records(
        DatabaseName=database_name,
        TableName=table_name,
        CommonAttributes={
            'Time': int(time()),
            'TimeUnit': 'SECONDS'
        },
        Records=records,
    )


if __name__ == "__main__":
    event = [{'Location': 'P+R RAI', 'Availability': 0}, {'Location': 'P+R Johan Cruijff ArenA', 'Availability': 1852}, {'Location': 'P+R Zeeburg 3', 'Availability': 179}, {'Location': 'P+R Noord', 'Availability': 161}, {'Location': "P+R Boven 't Y", 'Availability': 141}, {'Location': 'P+R Bos en Lommer', 'Availability': 88}, {'Location': 'P+R Zeeburg 2', 'Availability': 85}, {'Location': 'P+R Olympisch Stadion', 'Availability': 68}, {'Location': 'P+R Sloterdijk', 'Availability': 63}, {'Location': 'P+R Zeeburg 1', 'Availability': 56}, {'Location': 'Weekend P+R VUmc', 'Availability': 0}]
    response = handler(event, None)
    print(response)
