import requests
from xextract import String, Group

parser = Group(
    css='#currentAvailability tbody tr',
    children=[
        String(
            name='name',
            css='td:first-child',
            quant=1,
            callback=lambda string: string.strip('\r\n '),
        ),
        String(
            name='number',
            css='td:last-child',
            quant=1,
            callback=lambda string: 0 if string == '' else int(string.replace('.', '')),
        ),
    ]
)


def handler(event, context):
    response = requests.get(event['url'])
    return parser.parse(response.text)


if __name__ == "__main__":
    response = handler({'url':'https://penr.stachanov.com/penr/currentAvailability/'}, None)
    print(response)
