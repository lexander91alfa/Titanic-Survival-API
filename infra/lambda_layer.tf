resource "null_resource" "build_lambda_layer" {
  triggers = {
    requirements_hash = filemd5("../api/requirements.txt")
  }

  provisioner "local-exec" {
    command = "python ../build_layer.py"
  }
}

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "../.build/lambda_layer" 
  output_path = ".terraform/lambda_layer.zip"
  depends_on  = [null_resource.build_lambda_layer]
}

resource "aws_s3_object" "lambda_layer_zip" {
  bucket = aws_s3_bucket.lambda_artifacts.id
  key    = "layers/${local.project_name}-dependencies-layer.zip"
  source = data.archive_file.layer_zip.output_path
  
  etag = data.archive_file.layer_zip.output_md5

  depends_on = [data.archive_file.layer_zip]
}

resource "aws_lambda_layer_version" "python_dependencies_layer" {
  layer_name        = "${local.project_name}-dependencies-layer"
  s3_bucket         = aws_s3_bucket.lambda_artifacts.id
  s3_key            = aws_s3_object.lambda_layer_zip.key

  source_code_hash  = data.archive_file.layer_zip.output_base64sha256

  compatible_architectures = local.lambda.architectures
  compatible_runtimes = ["python3.12", "python3.11", "python3.10"]
  depends_on = [aws_s3_object.lambda_layer_zip]
}
