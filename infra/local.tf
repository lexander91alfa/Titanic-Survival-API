locals {
    project_name = "titanic-survival-api"
    environment  = "production"
    region       = "us-east-1"
    account_id   = data.aws_caller_identity.current.account_id

    lambda = {
        timeout      = 30
        memory_size  = 128
        runtime      = "python3.12"
        handler      = "prediction_handler.lambda_handler"
        function_name = "${local.project_name}-prediction-function"
        description = "Lambda function for Titanic survival prediction"
        architectures = ["arm64"]
    }

    dynamodb = {
        billing_mode   = "PAY_PER_REQUEST"
        table_name    = "${local.project_name}-passengers"
    }

    api_gateway = {
        name = "${local.project_name}-api-gateway"
        description = "API Gateway for Titanic Survival Prediction"
        stage_name = "v1"
    }

    tags = {
        Environment = local.environment
        Project     = local.project_name
    }

    endpoints = {
        sobreviventes_post    = { resource = aws_api_gateway_resource.sobreviventes.id, http_method = "POST" }
        sobreviventes_get     = { resource = aws_api_gateway_resource.sobreviventes.id, http_method = "GET" }
        sobreviventes_id_get  = { resource = aws_api_gateway_resource.sobreviventes_id.id, http_method = "GET" }
        sobreviventes_id_delete = { resource = aws_api_gateway_resource.sobreviventes_id.id, http_method = "DELETE" }
        health_get          = { resource = aws_api_gateway_resource.health.id, http_method = "GET", api_key_required = true }
    }
}