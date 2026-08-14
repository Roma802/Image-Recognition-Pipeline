import json
import urllib.parse
import boto3
import os

# Initialize AWS clients outside the handler for connection reuse across invocations
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

# Retrieve DynamoDB table name from environment variables
TABLE_NAME = os.environ.get('TABLE_NAME')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    # Extract bucket name and object key from the incoming S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        # Detect labels using Amazon Rekognition
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            MaxLabels=10,
            MinConfidence=70
        )
        
        # Extract detected label names
        labels = [label['Name'] for label in response['Labels']]

        
        # Save metadata and detected labels to DynamoDB
        table.put_item(
            Item={
                'imageId': key,
                'labels': labels,
                'bucket': bucket,
            }
        )
        print('successfully')
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully processed {key}')
        }
    except Exception as e:
        print(e)
        raise e
