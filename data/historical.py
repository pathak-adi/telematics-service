import json
import os
from boto3.dynamodb.conditions import Key, Attr
import boto3
import decimal
import json

dynamodb = boto3.resource('dynamodb')


# This is a workaround for: http://bugs.python.org/issue16535
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)


def query_by_time(event, context):
    table_name = os.environ['TELEMATICS_TABLE']
    table = dynamodb.Table(table_name)

    result = table.query(
        KeyConditionExpression=Key('imei').eq(event['pathParameters']['imei']) & Key('datetime').between(
            event['pathParameters']['start'],
            event['pathParameters']['end']),
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
