# ===================================================================
#  Configuração do API Gateway (HTTP API v2)
# ===================================================================
#
# Este bloco de código cria um endpoint HTTP público que aciona
# a nossa função Lambda do Titanic. Usamos a HTTP API (v2) por ser
# mais simples e barata que a REST API (v1) para integrações proxy.

# 1. O recurso principal da API
# Define o container para nossas rotas e integrações.
resource "aws_apigatewayv2_api" "http_api" {
  name          = local.api_gateway.name
  protocol_type = "HTTP"
  description   = local.api_gateway.description

  # Define uma política de CORS para permitir que a API
  # seja chamada a partir de navegadores em outros domínios.
  cors_configuration {
    allow_origins = ["*"] # Para produção, restrinja a domínios específicos
    allow_methods = ["POST", "GET", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization", "X-API-Key"]
    max_age       = 300
  }

  tags = local.tags
}

# 2. A Integração com a Lambda
# Este recurso é a "cola" que conecta o API Gateway à função Lambda.
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY" # Tipo padrão para passar toda a requisição
  
  # IMPORTANTE: Apontamos para o ARN de invocação (invoke_arn) do ALIAS da Lambda.
  # Isso garante que estamos sempre a invocar a versão mais recente e publicada
  # que tem o snapshot do SnapStart, e não a versão $LATEST.
  integration_uri = aws_lambda_alias.prediction_current.invoke_arn

  # O formato do payload que a Lambda receberá. 2.0 é o padrão para HTTP APIs.
  payload_format_version = "2.0" 
}

# 3. As Rotas da API
# Define quais métodos HTTP e caminhos (path) acionam a nossa integração.

# Rota para criar nova predição (POST /sobreviventes)
resource "aws_apigatewayv2_route" "post_sobreviventes" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /sobreviventes"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Rota para listar todas as predições (GET /sobreviventes)
resource "aws_apigatewayv2_route" "get_all_sobreviventes" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /sobreviventes"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Rota para buscar uma predição específica (GET /sobreviventes/{id})
resource "aws_apigatewayv2_route" "get_one_sobrevivente" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /sobreviventes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Rota para deletar uma predição (DELETE /sobreviventes/{id})
resource "aws_apigatewayv2_route" "delete_sobrevivente" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "DELETE /sobreviventes/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Rota para health check (GET /health)
resource "aws_apigatewayv2_route" "get_health" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /health"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# 4. Stage da API (equivalente ao deployment na REST API)
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

# 5. Permissão para o API Gateway Invocar a Lambda
# É crucial dar permissão explícita para o serviço do API Gateway
# poder executar a nossa função Lambda.
resource "aws_lambda_permission" "api_gw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  
  # A permissão é dada à função...
  function_name = aws_lambda_function.prediction.function_name
  # ...mas especificamente para o alias "current".
  qualifier     = aws_lambda_alias.prediction_current.name
  
  principal     = "apigateway.amazonaws.com"

  # O source_arn restringe a invocação para vir apenas desta API específica,
  # o que é uma boa prática de segurança.
  source_arn = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

# 6. Logs
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${local.project_name}"
  retention_in_days = 1

  tags = local.tags
}

# 7. Output da URL da API
# Este output irá mostrar a URL final da sua API no terminal
# após a execução do `terraform apply`.
output "api_endpoint" {
  description = "URL do endpoint da API para predição"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}