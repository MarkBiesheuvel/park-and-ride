#!/usr/bin/env python3
from boto3 import client
from os import environ

if 'DATABASE_NAME' not in environ or 'TABLE_NAME' not in environ:
    exit('Environment variables not set')

database_name = environ['DATABASE_NAME']
table_name = environ['TABLE_NAME']
timestream = client('timestream-query')
paginator = timestream.get_paginator('query')


class Query:

    def __init__(self, database, table):
        self.__database = database
        self.__table = table
        self.__columns = {}
        self.__where = []

    def columns(self, **kwargs):
        self.__columns = kwargs

        # Return self to chain functions
        return self

    def location(self, name):
        # TODO: escape value to avoid SQL injection
        self.__where.append(
            "Location = '{name}'".format(
                name=name
            )
        )

        # Return self to chain functions
        return self

    def time_range(self, start, end):
        self.__where.append(
            "time BETWEEN {function}('{start}') AND {function}('{end}')".format(
                function='from_iso8601_timestamp',
                start=start,
                end=end
            )
        )

        # Return self to chain functions
        return self

    def __str__(self):
        return 'SELECT {columns} FROM "{database}"."{table}" WHERE {where}'.format(
            database=self.__database,
            table=self.__table,
            where=' AND '.join(self.__where),
            columns=', '.join(
                '{expresion} AS {alias} '.format(
                    expresion=expresion,
                    alias=alias
                )
                for alias, expresion in self.__columns.items()
            )
        )


def process_row(row, columns):
    return {
        column['Name']: cell['ScalarValue']
        for cell, column in zip(row, columns)
    }


def handler(event, context):
    # TODO: make location name and time range variable
    query = Query(
        database=database_name,
        table=table_name
    ).columns(
        time="date_trunc('minute', time)",
        availability='measure_value::bigint'
    ).location(
        name='P+R Noord'
    ).time_range(
        start='2022-06-20T07:00:00',
        end='2022-06-20T11:59:59'
    )

    response_iterator = paginator.paginate(
        QueryString=str(query)
    )

    return [
        process_row(row['Data'], response['ColumnInfo'])
        for response in response_iterator
        for row in response['Rows']
    ]
