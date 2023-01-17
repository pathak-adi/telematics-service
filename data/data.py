import json
import logging
import os
import time
import uuid

import boto3

dynamodb = boto3.resource('dynamodb')


def insert(event, context):
    table_name = os.environ['TELEMATICS_TABLE']
    data = json.loads(event['body'])
    table = dynamodb.Table(table_name)

    item = {
        'datetime': data['datetime'],
        'imei': data['imei'],
        'data': data['data'],
    }

    # write the invoice to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(item)
    }

    return response