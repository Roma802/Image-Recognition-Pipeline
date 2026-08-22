import json
import boto3
import os
from botocore.config import Config

# Retrieve environment variables
S3_REGION = os.environ.get('S3_REGION', 'eu-central-1')

# Initialize S3 client with SigV4 for secure presigned URLs
s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    config=Config(signature_version='s3v4')
)

# Retrieve DynamoDB table name from environment variables 
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Extract query parameters from the API Gateway event
        query_params = event.get('queryStringParameters') or {}
        image_id = query_params.get('imageId')

        # Validate required query parameter
        if not image_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required query parameter: imageId'}),
            }

        # Retrieve image metadata from DynamoDB
        response = table.get_item(Key={'imageId': image_id})
        item = response.get('Item')

        # Handle case where image record does not exist
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Image not found or not processed yet'}),
            }

        bucket_name = item.get('bucket')

        # Generate a presigned URL to view the image
        image_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': image_id},
            ExpiresIn=3600,
        )

        # Return concise result for the requested image
        result = {'imageId': image_id, 'labels': item.get('labels', []), 'imageUrl': image_url}

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
            },
            'body': json.dumps(result),
        }
    
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
        
       
