#!/usr/bin/env python3
from constructs import Construct
from aws_cdk import (
    aws_timestream  as timestream,
)


class Datastore(Construct):

    def __init__(self, scope: Construct, id: str, database: timestream.CfnDatabase, table: timestream.CfnTable, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # TODO: migrate to L2 constructs when available

        self.database_name = database.ref
        self.table_name = table.attr_name
        self.table_arn = table.attr_arn