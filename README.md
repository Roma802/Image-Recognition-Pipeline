# Image-Recognition-Pipeline
Event-driven serverless image processing architecture built with AWS Lambda, API Gateway, S3, and AWS SAM.

```mermaid
Here is the updated Mermaid sequence diagram with all labels, comments, and actors translated into English:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client
    participant APIGW as API Gateway
    participant L1 as Lambda 1 (GenerateUploadUrl)
    participant S3 as Amazon S3
    participant L2 as Lambda 2 (ProcessImage)
    participant Rekog as AWS Rekognition
    participant DDB as DynamoDB (ImageLabels)
    participant L3 as Lambda 3 (GetImageLabels)

    box RGB(240, 244, 248) 1. File Upload
        Client->>APIGW: POST /upload
        APIGW->>L1: Invoke lambda_handler
        L1-->>APIGW: 200 OK (body: presignedUrl)
        APIGW-->>Client: Presigned PUT URL
        Client->>S3: Direct Upload (PUT /uploads/file.jpg)
    end

    box RGB(240, 248, 240) 2. AI Processing
        S3->>L2: Trigger: s3:ObjectCreated
        L2->>Rekog: detect_labels(Bucket, Key)
        Rekog-->>L2: Detected Labels
        L2->>DDB: put_item(imageId, labels, bucket)
    end

    box RGB(248, 240, 248) 3. Data Retrieval
        Client->>APIGW: GET /images?imageId=uploads/...
        APIGW->>L3: Invoke lambda_handler
        L3->>DDB: get_item(Key={'imageId': image_id})
        DDB-->>L3: Return Item (labels, bucket)
        Note over L3: Generate Presigned GET URL locally via SDK (boto3)
        L3-->>APIGW: 200 OK (body: imageId, labels, imageUrl)
        APIGW-->>Client: JSON Response (labels & imageUrl)
    end

```
```
