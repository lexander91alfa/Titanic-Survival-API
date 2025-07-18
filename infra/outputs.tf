output "api_base_url" {
  description = "URL base da API para invocação"
  value       = "https://${aws_api_gateway_rest_api.api.id}.execute-api.${data.aws_region.current.region}.amazonaws.com/${aws_api_gateway_stage.api_stage.stage_name}"
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.passengers.name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.prediction.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.prediction.arn
}