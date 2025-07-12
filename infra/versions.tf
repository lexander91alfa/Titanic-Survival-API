terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.2"
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
