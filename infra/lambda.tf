resource "aws_lambda_function" "prediction" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    =    local.lambda.function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = local.lambda.handler
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = local.lambda.runtime
  architectures   = local.lambda.architectures
  description     = local.lambda.description
  timeout         = local.lambda.timeout
  memory_size     = local.lambda.memory_size
  layers          = [aws_lambda_layer_version.python_dependencies_layer.arn]

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.passengers.name
      LOG_LEVEL          = "INFO"
    }
  }

  publish = true

  snap_start {
    apply_on = "PublishedVersions"
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }

  tags = local.tags

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_policy_attachment,
    aws_lambda_layer_version.python_dependencies_layer
  ]
}

resource "aws_lambda_alias" "production" {
  name             = "production"
  function_name    = aws_lambda_function.prediction.function_name
  function_version = aws_lambda_function.prediction.version
  
  lifecycle {
    ignore_changes = [function_version]
  }
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${local.lambda.function_name}"
  retention_in_days = 1
  tags = local.tags
}

resource "aws_sqs_queue" "lambda_dlq" {
  name                      = "${local.project_name}-lambda-dlq"
  message_retention_seconds = 86400
  
  tags = local.tags
}