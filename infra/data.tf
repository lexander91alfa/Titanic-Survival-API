data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../api"
  output_path = ".terraform/lambda_function.zip"
  excludes    = [
    "**/*.pyc",
    "**/__pycache__/**",
    "__pycache__/**",
    "**/.pytest_cache/**",
    ".pytest_cache/**",
    "requirements*.txt",
    "tests/**",
    "**/*.ipynb",
    ".venv/**",
    "**/.venv/**", 
    ".env",
    "**/.env",
    ".coverage",
    "**/.coverage",
    ".vscode/**",
    "**/.vscode/**",
    "mock_api/**",
    "**/mock_api/**",
    ".coverage/**",
    "**/.coverage/**",
    "api_mock.py",
    "tests/**",
    "**/tests/**",
    "models/**",
    "**/models/**",
  ]
}

# Add a null resource to trigger rebuild when source files change
resource "null_resource" "lambda_source_trigger" {
  triggers = {
    source_hash = sha256(join("", [
      for file in fileset("../api/src", "**/*.py") : filemd5("../api/src/${file}")
    ]))
    handler_hash = filemd5("../api/prediction_handler.py")
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}