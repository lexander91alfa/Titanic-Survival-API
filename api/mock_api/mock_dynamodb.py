import boto3
import os


def create_table():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName=os.environ["DYNAMODB_TABLE_NAME"],
        KeySchema=[{"AttributeName": "passenger_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "passenger_id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    return table
