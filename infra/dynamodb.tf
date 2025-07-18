resource "aws_dynamodb_table" "passengers" {
  name           = local.dynamodb.table_name
  billing_mode   = local.dynamodb.billing_mode
  hash_key       = "passenger_id"

  attribute {
    name = "passenger_id"
    type = "S"
  }

  tags = local.tags
}

resource "aws_cloudwatch_log_group" "dynamodb_logs" {
  name              = "/aws/dynamodb/${aws_dynamodb_table.passengers.name}"
  retention_in_days = 1

  tags = local.tags
}