# Aws Ecs Worker Template


## Requirements

- AWS CDK
- AWS cli
- AWS User with permissions
- Docker / Docker-compose
- Python3.7


## Initial setup

### Deploy Cloudformation stack using CDK (initial setup only)
- The `ServiceStack` creates the following resources:
    - ECR Repository (empty)
    - SQS Queue and Dead-Letter-Queue
    - CloudWatch Alarm
    - ECS Task Definition (with QUEUE_NAME as environment variable)
    - ECS Service, with AutoScalling
    - Task Definition and Task role and policies
    - Log Group


## Step by Step

### 1. Build and push image to ECR


### 2. CDK Deploy service



### Testing

    ```bash
    aws sqs create-queue \
            --queue-name test-my-worker
    ```
