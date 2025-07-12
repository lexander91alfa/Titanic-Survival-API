locals {
    project_name = "titanic-survival-api"
    environment  = "production"
    region       = "us-west-2"
    tags = {
        Environment = local.environment
        Project     = local.project_name
    }

    lambda = {
        timeout      = 30
        memory_size  = 128
        runtime      = "python3.12"
        handler      = "prediction_handler.lambda_handler"
        function_name = "${local.project_name}-prediction-function"
    }

    dynamodb = {
        billing_mode   = "PAY_PER_REQUEST"
        table_name    = "${local.project_name}-passengers"
    }
}