import json
import boto3
import uuid
import os

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def lambda_handler(event, context):
    try:
        # Parse the request body from the client
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('file_name', 'image.jpg')
        content_type = body.get('content_type', 'image/jpeg')
        
        # Generate a unique S3 key to prevent file overwrites
        file_extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
        object_key = f"uploads/{uuid.uuid4()}.{file_extension}"
        
        # Generate a presigned URL for the put_object operation
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': object_key,
                'ContentType': content_type
            },
            ExpiresIn=300  
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'upload_url': presigned_url,
                'object_key': object_key
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
