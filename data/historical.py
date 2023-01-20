import logging
import os
from boto3.dynamodb.conditions import Key, Attr
import boto3
import decimal
import json

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


def query_by_time(event, context):
    table_name = os.environ['TELEMATICS_TABLE']
    table = dynamodb.Table(table_name)
    logger.info(f'Event Body {event}')
    logger.info(event['pathParameters']['start'])
    logger.info(event['pathParameters']['end'])
    logger.info(event['pathParameters']['imei'])
    result = table.query(
        KeyConditionExpression=Key('imei').eq(str(event['pathParameters']['imei'])) & Key('datetime').between(
            int(event['pathParameters']['start']),
            int(event['pathParameters']['end'])),
    )
    if result['Items']:

        # create a response
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(result['Items'], cls=DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 200,
            "body": json.dumps('No result', cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return response


def query_by_device(event, context):
    table_name = os.environ['TELEMATICS_TABLE']
    table = dynamodb.Table(table_name)
    logger.info(f'Event Body {event}')
    logger.info(event['pathParameters']['imei'])
    result = table.query(
        KeyConditionExpression=Key('imei').eq(str(event['pathParameters']['imei']))
    )

    if result['Items']:

        # create a response
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(result['Items'], cls=DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 200,
            "body": json.dumps('No result', cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return response
