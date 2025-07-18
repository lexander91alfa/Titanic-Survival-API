resource "aws_s3_bucket" "lambda_artifacts" {
    bucket = "${local.project_name}-lambda-artifacts-${local.account_id}-prod-v1"

    force_destroy = true
    tags = local.tags
}

resource "aws_s3_bucket_public_access_block" "lambda_artifacts_public_access" {
  bucket = aws_s3_bucket.lambda_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_artifacts_encryption" {
  bucket = aws_s3_bucket.lambda_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lambda_artifacts_lifecycle" {
  bucket = aws_s3_bucket.lambda_artifacts.id

  rule {
    id      = "expire-old-noncurrent-versions"
    status  = "Enabled"

    filter {
      prefix = "layers/"
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}