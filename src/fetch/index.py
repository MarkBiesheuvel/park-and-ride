#!/usr/bin/env python3
import requests
from xextract import String, Group

parser = Group(
    css='#currentAvailability tbody tr',
    children=[
        String(
            name='Location',
            css='td:first-child',
            quant=1,
            callback=lambda string: string.strip('\r\n '),
        ),
        String(
            name='Availability',
            css='td:last-child',
            quant=1,
            callback=lambda string: 0 if string == '' else int(string.replace('.', '')),
        ),
    ]
)


def handler(event, context):
    response = requests.get(event['url'])
    return parser.parse(response.text)
