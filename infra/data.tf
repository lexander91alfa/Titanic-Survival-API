data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../app/lambda"
  output_path = "${path.module}/lambda_function.zip"
  excludes    = ["*.pyc", "__pycache__", "*.txt"]
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}