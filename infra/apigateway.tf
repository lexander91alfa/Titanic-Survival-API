# ===================================================================
# 1. Definição da API REST
# ===================================================================
resource "aws_api_gateway_rest_api" "titanic_api" {
  name        = local.api_gateway.name
  description = local.api_gateway.description
}

# ===================================================================
# 2. Criação dos Recursos (Endpoints)
# ===================================================================
resource "aws_api_gateway_resource" "sobreviventes" {
  parent_id   = aws_api_gateway_rest_api.titanic_api.root_resource_id
  path_part   = "sobreviventes"
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id

  depends_on = [aws_api_gateway_rest_api.titanic_api]
}

resource "aws_api_gateway_resource" "sobrevivente_id" {
  parent_id   = aws_api_gateway_resource.sobreviventes.id
  path_part   = "{id}"
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id

  depends_on = [aws_api_gateway_resource.sobreviventes]
}

# ===================================================================
# 3. Métodos HTTP e Integração com a Lambda
# ===================================================================

resource "aws_api_gateway_method" "post_sobreviventes" {
  rest_api_id   = aws_api_gateway_rest_api.titanic_api.id
  resource_id   = aws_api_gateway_resource.sobreviventes.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true

}

resource "aws_api_gateway_integration" "post_sobreviventes_lambda" {
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id
  resource_id = aws_api_gateway_resource.sobreviventes.id
  http_method = aws_api_gateway_method.post_sobreviventes.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.prediction.invoke_arn

  depends_on = [aws_api_gateway_method.post_sobreviventes, aws_lambda_function.prediction]
}

resource "aws_api_gateway_method" "get_all_sobreviventes" {
  rest_api_id    = aws_api_gateway_rest_api.titanic_api.id
  resource_id    = aws_api_gateway_resource.sobreviventes.id
  http_method    = "GET"
  authorization  = "NONE"
  api_key_required = true

}

resource "aws_api_gateway_integration" "get_all_sobreviventes_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.titanic_api.id
  resource_id             = aws_api_gateway_resource.sobreviventes.id
  http_method             = aws_api_gateway_method.get_all_sobreviventes.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.prediction.invoke_arn

  depends_on = [aws_api_gateway_method.get_all_sobreviventes, aws_lambda_function.prediction]
}

resource "aws_api_gateway_method" "get_one_sobrevivente" {
  rest_api_id    = aws_api_gateway_rest_api.titanic_api.id
  resource_id    = aws_api_gateway_resource.sobrevivente_id.id
  http_method    = "GET"
  authorization  = "NONE"
  api_key_required = true

  depends_on = [aws_api_gateway_resource.sobrevivente_id]
}

resource "aws_api_gateway_integration" "get_one_sobrevivente_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.titanic_api.id
  resource_id             = aws_api_gateway_resource.sobrevivente_id.id
  http_method             = aws_api_gateway_method.get_one_sobrevivente.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.prediction.invoke_arn

  depends_on = [aws_api_gateway_method.get_one_sobrevivente, aws_lambda_function.prediction]
}

resource "aws_api_gateway_method" "delete_sobrevivente" {
  rest_api_id    = aws_api_gateway_rest_api.titanic_api.id
  resource_id    = aws_api_gateway_resource.sobrevivente_id.id
  http_method    = "DELETE"
  authorization  = "NONE"
  api_key_required = true

  depends_on = [aws_api_gateway_resource.sobrevivente_id]
}

resource "aws_api_gateway_integration" "delete_sobrevivente_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.titanic_api.id
  resource_id             = aws_api_gateway_resource.sobrevivente_id.id
  http_method             = aws_api_gateway_method.delete_sobrevivente.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.prediction.invoke_arn

  depends_on = [aws_api_gateway_method.delete_sobrevivente, aws_lambda_function.prediction]
}

resource "aws_api_gateway_resource" "docs" {
  parent_id   = aws_api_gateway_rest_api.titanic_api.root_resource_id
  path_part   = "docs"
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id
}

resource "aws_api_gateway_method" "get_docs" {
  rest_api_id      = aws_api_gateway_rest_api.titanic_api.id
  resource_id      = aws_api_gateway_resource.docs.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

# ===================================================================
# 4. Deploy da API
# ===================================================================
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.titanic_api.id

  triggers = {
    redeployment = sha1(jsonencode(
      [
        aws_api_gateway_resource.sobreviventes.id,
        aws_api_gateway_resource.sobrevivente_id.id,
        aws_api_gateway_method.post_sobreviventes.id,
        aws_api_gateway_method.get_all_sobreviventes.id,
        aws_api_gateway_method.get_one_sobrevivente.id,
        aws_api_gateway_method.delete_sobrevivente.id,
        aws_api_gateway_integration.post_sobreviventes_lambda.id,
        aws_api_gateway_integration.get_all_sobreviventes_lambda.id,
        aws_api_gateway_integration.get_one_sobrevivente_lambda.id,
        aws_api_gateway_integration.delete_sobrevivente_lambda.id,
      ]
    ))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.post_sobreviventes_lambda,
    aws_api_gateway_integration.get_all_sobreviventes_lambda,
    aws_api_gateway_integration.get_one_sobrevivente_lambda,
    aws_api_gateway_integration.delete_sobrevivente_lambda
  ]
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.titanic_api.id
  stage_name    = local.api_gateway.stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId    = "$context.requestId"
      ip           = "$context.identity.sourceIp"
      caller       = "$context.identity.caller"
      user         = "$context.identity.user"
      requestTime  = "$context.requestTime"
      httpMethod   = "$context.httpMethod"
      resourcePath = "$context.resourcePath"
      status       = "$context.status"
      protocol     = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = local.tags

  depends_on = [
    aws_api_gateway_deployment.api_deployment,
    aws_cloudwatch_log_group.api_gateway_logs,
    aws_api_gateway_account.api_gateway_account
  ]
}

# ===================================================================
# 5. Permissão para a Lambda
# ===================================================================
resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.prediction.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.titanic_api.execution_arn}/*/*"
}

# ===================================================================
# 6. Segurança: API Key e Usage Plan (Throttling)
# ===================================================================
resource "aws_api_gateway_api_key" "case_api_key" {
  name = "api_key_api_titanic_survival"
}

resource "aws_api_gateway_usage_plan" "case_usage_plan" {
  name = "plan_to_limit_api_usage"
  description = "Plano para limitar o uso da API do case"

  api_stages {
    api_id = aws_api_gateway_rest_api.titanic_api.id
    stage  = aws_api_gateway_stage.api_stage.stage_name
  }

  throttle_settings {
    burst_limit = 5
    rate_limit  = 10
  }

  quota_settings {
    limit  = 100
    period = "DAY"
  }

  depends_on = [aws_api_gateway_stage.api_stage]
}

resource "aws_api_gateway_usage_plan_key" "case_plan_key" {
  key_id        = aws_api_gateway_api_key.case_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.case_usage_plan.id

  depends_on = [aws_api_gateway_api_key.case_api_key, aws_api_gateway_usage_plan.case_usage_plan]
}

# ===================================================================
# 7. Logs
# ===================================================================

resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.project_name}"
  retention_in_days = 1

  tags = local.tags
}

resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn

  depends_on = [aws_iam_role_policy_attachment.api_gateway_cloudwatch_attachment]
}