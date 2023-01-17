import json
import os
import decimalencoder
from boto3.dynamodb.conditions import Key, Attr
import boto3

dynamodb = boto3.resource('dynamodb')


def query_by_time(event, context):

    table_name = os.environ['TELEMATICS_TABLE']
    table = dynamodb.Table(table_name)

    result = table.query(
        KeyConditionExpression=Key('datetime').between(event['pathParameters']['start'],
                                                   event['pathParameters']['end']) & Key('imei').eq(event['pathParameters']['imei']),
    )
    if result['Items']:

        # create a response
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(result['Items'],
                               cls=decimalencoder.DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 200,
            "body": json.dumps('No result',
                               cls=decimalencoder.DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return response