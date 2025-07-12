terraform {
  required_version = ">= 1.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
    region = "us-west-2"
    default_tags {
        tags = {
            Environment = "production"
            Project     = "infra"
        }
    }
}
