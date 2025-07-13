resource "null_resource" "install_lambda_dependencies" {
  triggers = {
    requirements_md5 = filemd5("../api/requirements.txt")
  }

  provisioner "local-exec" {
    command = "pip install -r ../api/requirements.txt -t ../api/"
  }
}


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../api"
  output_path = ".terraform/lambda_function.zip"
  excludes    = [
    "*.pyc",
    "__pycache__",
    "*.txt",
    "tests",
    "tests/*",
    "models/treinamento.ipynb",
    ".venv",
    ".venv/*",
    ".env",
    ".env/*",
  ]

  depends_on = [null_resource.install_lambda_dependencies]
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}