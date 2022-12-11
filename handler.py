import json
import os
import logging
import boto3
import botocore
import sys

# sys.path.insert(0, F"{os.environ['LAMBDA_TASK_ROOT']}/{os.environ['DIR_NAME']}")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.resource('dynamodb')
connections = dynamodb.Table(os.environ['WEBSOCKETS_TABLE'])


def connect(event, context):
    logger.debug("onconnect: %s" % event)

    connection_id = event['requestContext']['connectionId']
    if connection_id is None:
        return {'statusCode': 400,
                'body': 'bad request'}

    result = connections.put_item(Item={'connection_id': connection_id})
    if result.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
        return {'statusCode': 500,
                'body': 'something went wrong'}
    return {'statusCode': 200,
            'body': 'ok'}


def disconnect(event, context):
    logger.debug("ondisconnect: %s" % event)

    connection_id = event['requestContext']['connectionId']
    if connection_id is None:
        return {'statusCode': 400,
                'body': 'bad request'}

    result = connections.delete_item(Key={'connection_id': connection_id})
    if result.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
        logger.debug('delete_item failed: %s' % result)
    return {'statusCode': 200,
            'body': 'ok'}


def send_message(event, context):
    logger.debug("sendmessage: %s" % event)
    try:
        post_data = json.loads(event.get('body', '{}')).get('data')
    except:
        post_data=event['body']
    domain_name = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    if (post_data and domain_name and stage) is None:
        return {'statusCode': 400,
                'body': 'bad request'}

    items = connections.scan(ProjectionExpression='connection_id').get('Items')
    if items is None:
        return {'statusCode': 500,
                'body': 'something went wrong'}

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")
    for item in items:
        try:
            _ = apigw_management.post_to_connection(ConnectionId=item['connection_id'],
                                                    Data=post_data)
        except botocore.exceptions.ClientError as e:
            if e.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 410:
                connections.delete_item(Key={'connection_id': item['connection_id']})
                logger.debug('post_to_connection skipped: %s removed from connections' % item['connection_id'])
            else:
                logger.debug('post_to_connection failed: %s' % e)
                return {'statusCode': 500,
                        'body': 'something went wrong'}
    return {'statusCode': 200,
            'body': 'ok'}
