# ===================================================================
# API Gateway (REST API)
# ===================================================================

resource "aws_api_gateway_rest_api" "api" {
  name        = local.project_name
  description = "API para demonstrar autorização com API Key"
  tags        = local.tags
}

# ===================================================================
# API routes
# ===================================================================

resource "aws_api_gateway_resource" "sobreviventes" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "sobreviventes"
}

resource "aws_api_gateway_resource" "sobreviventes_id" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.sobreviventes.id
  path_part   = "{id}"
}

resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "health"
}

# ===================================================================
# API Methods
# ===================================================================

resource "aws_api_gateway_method" "all" {
  for_each = local.endpoints

  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = each.value.resource
  http_method   = each.value.http_method
  authorization = "NONE"
  api_key_required = lookup(each.value, "api_key_required", true)
}

# ===================================================================
# API Integrations
# ===================================================================

resource "aws_api_gateway_integration" "all" {
  for_each = local.endpoints

  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = each.value.resource
  http_method             = aws_api_gateway_method.all[each.key].http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.prediction.invoke_arn
}

# ===================================================================
# API Deployment and Stage
# ===================================================================

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  description = "Deployment for v1 stage"

  triggers = {
    redeployment = sha1(jsonencode(values(aws_api_gateway_integration.all)[*].id))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "v1"
  tags          = local.tags
}

# ===================================================================
# API Key e Usage Plan
# ===================================================================

resource "aws_api_gateway_api_key" "main_key" {
  name = "${local.project_name}-key"
  tags = local.tags
}

resource "aws_api_gateway_usage_plan" "main_plan" {
  name = "${local.project_name}-plan"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_stage.api_stage.stage_name
  }
  
  quota_settings {
    limit  = 100
    period = "DAY"
  }
  
  throttle_settings {
    rate_limit  = 5
    burst_limit = 10
  }
  tags = local.tags
}

resource "aws_api_gateway_usage_plan_key" "main_plan_key" {
  key_id        = aws_api_gateway_api_key.main_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.main_plan.id
}

# ===================================================================
# Permissões e Saídas
# ===================================================================

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.prediction.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}
