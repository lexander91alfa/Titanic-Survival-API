import json


def lambda_handler(event, context):
    # Your Lambda function code goes here
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from Lambda!"})
    }