data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../api"
  output_path = ".terraform/lambda_function.zip"
  excludes    = [
    "*.pyc",
    "__pycache__",
    "*.txt",
    "tests",
    "*.ipynb",
    ".venv",
    ".env",
  ]
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}