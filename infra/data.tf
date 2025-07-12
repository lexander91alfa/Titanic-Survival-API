data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../app"
  output_path = ".terraform/lambda_function.zip"
  excludes    = [
    "*.pyc",
    "__pycache__",
    "*.txt",
    "tests",
    "tests/*",
    "/models/treinamento.ipynb"
  ]
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}