resource "aws_lambda_function" "prediction" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    =    local.lambda.function_name
  role            = aws_iam_role.lambda_role.arn
  region         = local.region
  handler         = local.lambda.handler
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = local.lambda.runtime
  timeout         = local.lambda.timeout
  memory_size     = local.lambda.memory_size

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.passengers.name
    }
  }

  tags = local.tags

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_policy_attachment
  ]
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda.function_name}"
  retention_in_days = 1
  tags = local.tags
}