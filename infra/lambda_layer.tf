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

  depends_on = [null_resource.build_lambda_layer]
}

resource "aws_lambda_layer_version" "python_dependencies_layer" {
  layer_name        = "${local.project_name}-dependencies-layer"
  filename          = data.archive_file.layer_zip.output_path
  description       = "Lambda layer containing Python dependencies"
  compatible_architectures = local.lambda.architectures
  source_code_hash  = data.archive_file.layer_zip.output_base64sha256
  
  compatible_runtimes = ["python3.12", "python3.11", "python3.10"]
}


