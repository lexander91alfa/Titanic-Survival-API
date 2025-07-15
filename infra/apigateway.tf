# ===================================================================
#  Configuração do API Gateway (HTTP API v2)
# ===================================================================
resource "aws_apigatewayv2_api" "http_api" {
  name          = local.api_gateway.name
  protocol_type = "HTTP"
  description   = local.api_gateway.description

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-API-Key"]
    max_age       = 300
  }

  tags = local.tags
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  
  integration_uri = aws_lambda_alias.prediction_current.invoke_arn

  payload_format_version = "2.0" 
}

resource "aws_apigatewayv2_route" "post_sobreviventes" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /sobreviventes"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "get_all_sobreviventes" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /sobreviventes"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "get_one_sobrevivente" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /sobreviventes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "delete_sobrevivente" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "DELETE /sobreviventes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "get_health" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "api_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = local.api_gateway.stage_name
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId    = "$context.requestId"
      ip           = "$context.identity.sourceIp"
      requestTime  = "$context.requestTime"
      httpMethod   = "$context.httpMethod"
      routeKey     = "$context.routeKey"
      status       = "$context.status"
      protocol     = "$context.protocol"
      responseLength = "$context.responseLength"
      error        = "$context.error.message"
      errorType    = "$context.error.messageString"
    })
  }

  default_route_settings {
    throttling_burst_limit = 5
    throttling_rate_limit  = 10
  }

  tags = local.tags

  depends_on = [
    aws_cloudwatch_log_group.api_gateway_logs
  ]
}

resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  
  function_name = aws_lambda_function.prediction.function_name
  qualifier     = aws_lambda_alias.prediction_current.name
  
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.project_name}"
  retention_in_days = 1

  tags = local.tags
}

output "api_endpoint" {
  description = "URL do endpoint da API para predição"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}