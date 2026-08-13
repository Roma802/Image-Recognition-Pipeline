# Image-Recognition-Pipeline
Event-driven serverless image processing architecture built with AWS Lambda, API Gateway, S3, and AWS SAM.

# Image-Recognition-Pipeline

Event-driven serverless image processing architecture built with AWS Lambda, API Gateway, S3, DynamoDB, AWS Rekognition, and AWS SAM.

## Architecture

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

    box 1. File Upload
        participant Client
        participant APIGW
        participant L1
        participant S3
    end

    box 2. AI Processing
        participant L2
        participant Rekog
        participant DDB
    end

    box 3. Data Retrieval
        participant L3
    end

    Client->>APIGW: POST /generate-url ({file_name, content_type})
    APIGW->>L1: Invoke lambda_handler
    L1-->>APIGW: 200 OK (presignedUrl)
    APIGW-->>Client: Presigned PUT URL
    Client->>S3: Direct Upload (PUT image file)

    S3->>L2: Trigger: s3:ObjectCreated
    L2->>Rekog: Detect labels in image
    Rekog-->>L2: Detected Labels
    L2->>DDB: Save labels & bucket metadata

    Client->>APIGW: GET /images?imageId=...
    APIGW->>L3: Invoke lambda_handler
    L3->>DDB: Fetch labels & bucket by imageId
    DDB-->>L3: Return Image Metadata
    Note over L3: Generate viewable Presigned GET URL
    L3-->>APIGW: 200 OK (labels & imageUrl)
    APIGW-->>Client: JSON Response
