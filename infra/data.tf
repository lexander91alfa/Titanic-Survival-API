data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../app/lambda"
  output_path = "lambda_function.zip"
  excludes    = ["*.pyc", "__pycache__", "*.txt"]
}