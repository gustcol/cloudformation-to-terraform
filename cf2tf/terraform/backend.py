"""
Terraform Backend Configuration Generator

Generates secure, production-ready backend configurations for Terraform state management.
Supports S3 backend with DynamoDB locking, encryption, and versioning.
"""

from typing import Any, Dict, List, Optional


class BackendGenerator:
    """Generator for Terraform backend configurations."""

    def __init__(
        self,
        project_name: str,
        environment: str = "dev",
        aws_region: str = "us-east-1",
    ):
        """
        Initialize the BackendGenerator.

        Args:
            project_name: Name of the project (used for bucket naming).
            environment: Environment name (dev, staging, prod).
            aws_region: AWS region for the backend resources.
        """
        self.project_name = project_name.lower().replace("_", "-")
        self.environment = environment.lower()
        self.aws_region = aws_region

    def generate_s3_backend(
        self,
        bucket_name: Optional[str] = None,
        dynamodb_table: Optional[str] = None,
        encrypt: bool = True,
        kms_key_id: Optional[str] = None,
        workspace_key_prefix: Optional[str] = None,
    ) -> str:
        """
        Generate S3 backend configuration with DynamoDB locking.

        Args:
            bucket_name: S3 bucket name (auto-generated if not provided).
            dynamodb_table: DynamoDB table name for state locking.
            encrypt: Enable server-side encryption.
            kms_key_id: KMS key ID for encryption (uses AES256 if not provided).
            workspace_key_prefix: Prefix for workspace state files.

        Returns:
            Terraform backend configuration block.
        """
        bucket = bucket_name or f"{self.project_name}-terraform-state-{self.environment}"
        table = dynamodb_table or f"{self.project_name}-terraform-locks-{self.environment}"
        key = f"{self.environment}/terraform.tfstate"

        config = f'''terraform {{
  backend "s3" {{
    bucket         = "{bucket}"
    key            = "{key}"
    region         = "{self.aws_region}"
    encrypt        = {str(encrypt).lower()}
    dynamodb_table = "{table}"
'''

        if kms_key_id:
            config += f'    kms_key_id     = "{kms_key_id}"\n'

        if workspace_key_prefix:
            config += f'    workspace_key_prefix = "{workspace_key_prefix}"\n'

        config += '''
    # Recommended settings for production
    skip_metadata_api_check     = false
    skip_region_validation      = false
    skip_credentials_validation = false
  }
}
'''
        return config

    def generate_backend_resources_tf(
        self,
        bucket_name: Optional[str] = None,
        dynamodb_table: Optional[str] = None,
        kms_key_alias: Optional[str] = None,
        enable_replication: bool = False,
        replication_region: str = "us-west-2",
    ) -> str:
        """
        Generate Terraform code to create backend infrastructure.

        Args:
            bucket_name: S3 bucket name.
            dynamodb_table: DynamoDB table name.
            kms_key_alias: KMS key alias for encryption.
            enable_replication: Enable cross-region replication.
            replication_region: Region for bucket replication.

        Returns:
            Terraform configuration for backend resources.
        """
        bucket = bucket_name or f"{self.project_name}-terraform-state-{self.environment}"
        table = dynamodb_table or f"{self.project_name}-terraform-locks-{self.environment}"
        kms_alias = kms_key_alias or f"alias/{self.project_name}-terraform-{self.environment}"

        config = f'''# ==============================================================================
# Terraform State Backend Infrastructure
# Project: {self.project_name}
# Environment: {self.environment}
# ==============================================================================

# KMS Key for State Encryption
resource "aws_kms_key" "terraform_state" {{
  description             = "KMS key for Terraform state encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {{
    Name        = "{self.project_name}-terraform-state-key"
    Environment = "{self.environment}"
    ManagedBy   = "terraform"
    Purpose     = "terraform-state-encryption"
  }}
}}

resource "aws_kms_alias" "terraform_state" {{
  name          = "{kms_alias}"
  target_key_id = aws_kms_key.terraform_state.key_id
}}

# S3 Bucket for State Storage
resource "aws_s3_bucket" "terraform_state" {{
  bucket = "{bucket}"

  tags = {{
    Name        = "{bucket}"
    Environment = "{self.environment}"
    ManagedBy   = "terraform"
    Purpose     = "terraform-state"
  }}
}}

# Enable versioning for state history
resource "aws_s3_bucket_versioning" "terraform_state" {{
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {{
    status = "Enabled"
  }}
}}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {{
  bucket = aws_s3_bucket.terraform_state.id

  rule {{
    apply_server_side_encryption_by_default {{
      kms_master_key_id = aws_kms_key.terraform_state.arn
      sse_algorithm     = "aws:kms"
    }}
    bucket_key_enabled = true
  }}
}}

# Block all public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {{
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

# Lifecycle rules for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {{
  bucket = aws_s3_bucket.terraform_state.id

  rule {{
    id     = "state-lifecycle"
    status = "Enabled"

    noncurrent_version_transition {{
      noncurrent_days = 30
      storage_class   = "STANDARD_IA"
    }}

    noncurrent_version_transition {{
      noncurrent_days = 60
      storage_class   = "GLACIER"
    }}

    noncurrent_version_expiration {{
      noncurrent_days = 365
    }}
  }}
}}

# Bucket policy to enforce encryption and secure transport
resource "aws_s3_bucket_policy" "terraform_state" {{
  bucket = aws_s3_bucket.terraform_state.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid       = "EnforceTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.terraform_state.arn,
          "${{aws_s3_bucket.terraform_state.arn}}/*"
        ]
        Condition = {{
          Bool = {{
            "aws:SecureTransport" = "false"
          }}
        }}
      }},
      {{
        Sid       = "EnforceEncryption"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${{aws_s3_bucket.terraform_state.arn}}/*"
        Condition = {{
          StringNotEquals = {{
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }}
        }}
      }}
    ]
  }})
}}

# DynamoDB Table for State Locking
resource "aws_dynamodb_table" "terraform_locks" {{
  name         = "{table}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {{
    name = "LockID"
    type = "S"
  }}

  point_in_time_recovery {{
    enabled = true
  }}

  server_side_encryption {{
    enabled     = true
    kms_key_arn = aws_kms_key.terraform_state.arn
  }}

  tags = {{
    Name        = "{table}"
    Environment = "{self.environment}"
    ManagedBy   = "terraform"
    Purpose     = "terraform-state-locking"
  }}
}}
'''

        if enable_replication:
            config += f'''
# Cross-Region Replication for Disaster Recovery
resource "aws_s3_bucket" "terraform_state_replica" {{
  provider = aws.{replication_region.replace("-", "_")}
  bucket   = "{bucket}-replica"

  tags = {{
    Name        = "{bucket}-replica"
    Environment = "{self.environment}"
    ManagedBy   = "terraform"
    Purpose     = "terraform-state-replica"
  }}
}}

resource "aws_s3_bucket_versioning" "terraform_state_replica" {{
  provider = aws.{replication_region.replace("-", "_")}
  bucket   = aws_s3_bucket.terraform_state_replica.id

  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_iam_role" "replication" {{
  name = "{self.project_name}-terraform-state-replication"

  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "s3.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_s3_bucket_replication_configuration" "terraform_state" {{
  depends_on = [aws_s3_bucket_versioning.terraform_state]

  bucket = aws_s3_bucket.terraform_state.id
  role   = aws_iam_role.replication.arn

  rule {{
    id     = "terraform-state-replication"
    status = "Enabled"

    destination {{
      bucket        = aws_s3_bucket.terraform_state_replica.arn
      storage_class = "STANDARD"

      encryption_configuration {{
        replica_kms_key_id = aws_kms_key.terraform_state.arn
      }}
    }}

    source_selection_criteria {{
      sse_kms_encrypted_objects {{
        status = "Enabled"
      }}
    }}
  }}
}}
'''

        config += f'''
# ==============================================================================
# Outputs
# ==============================================================================

output "state_bucket_name" {{
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}}

output "state_bucket_arn" {{
  description = "ARN of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.arn
}}

output "dynamodb_table_name" {{
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}}

output "kms_key_arn" {{
  description = "ARN of the KMS key for state encryption"
  value       = aws_kms_key.terraform_state.arn
}}

output "backend_config" {{
  description = "Backend configuration to use in other projects"
  value = <<-EOT
    terraform {{
      backend "s3" {{
        bucket         = "${{aws_s3_bucket.terraform_state.id}}"
        key            = "<your-state-key>/terraform.tfstate"
        region         = "{self.aws_region}"
        encrypt        = true
        kms_key_id     = "${{aws_kms_key.terraform_state.arn}}"
        dynamodb_table = "${{aws_dynamodb_table.terraform_locks.name}}"
      }}
    }}
  EOT
}}
'''
        return config

    def generate_workspace_strategy(self) -> str:
        """
        Generate workspace strategy documentation and configuration.

        Returns:
            Terraform workspace configuration and best practices.
        """
        return f'''# ==============================================================================
# Terraform Workspace Strategy
# ==============================================================================

# Use workspaces for environment separation with shared configuration
# Recommended structure:
#
# project/
# ├── environments/
# │   ├── dev.tfvars
# │   ├── staging.tfvars
# │   └── prod.tfvars
# ├── main.tf
# ├── variables.tf
# ├── outputs.tf
# └── backend.tf

# Environment-specific variables
variable "environment" {{
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {{
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }}
}}

# Environment configuration map
locals {{
  env_config = {{
    dev = {{
      instance_type     = "t3.micro"
      min_capacity      = 1
      max_capacity      = 2
      multi_az          = false
      deletion_protection = false
      backup_retention  = 7
    }}
    staging = {{
      instance_type     = "t3.small"
      min_capacity      = 2
      max_capacity      = 4
      multi_az          = true
      deletion_protection = false
      backup_retention  = 14
    }}
    prod = {{
      instance_type     = "t3.medium"
      min_capacity      = 3
      max_capacity      = 10
      multi_az          = true
      deletion_protection = true
      backup_retention  = 30
    }}
  }}

  # Select configuration based on workspace or variable
  config = local.env_config[terraform.workspace != "default" ? terraform.workspace : var.environment]
}}

# Usage example:
# resource "aws_instance" "app" {{
#   instance_type = local.config.instance_type
#   ...
# }}
'''


class ImportGenerator:
    """Generator for terraform import commands."""

    def __init__(self):
        """Initialize the ImportGenerator."""
        self.imports: List[Dict[str, str]] = []

    def add_import(
        self,
        resource_type: str,
        resource_name: str,
        resource_id: str,
    ) -> "ImportGenerator":
        """
        Add a resource to import.

        Args:
            resource_type: Terraform resource type.
            resource_name: Local resource name.
            resource_id: AWS resource ID.

        Returns:
            Self for method chaining.
        """
        self.imports.append({
            "type": resource_type,
            "name": resource_name,
            "id": resource_id,
        })
        return self

    def generate_import_commands(self) -> str:
        """
        Generate terraform import commands.

        Returns:
            Shell script with import commands.
        """
        lines = [
            "#!/bin/bash",
            "# Terraform Import Commands",
            "# Generated by CF2TF",
            "",
            "set -e",
            "",
        ]

        for imp in self.imports:
            address = f'{imp["type"]}.{imp["name"]}'
            lines.append(f'terraform import {address} {imp["id"]}')

        return "\n".join(lines)

    def generate_import_blocks(self) -> str:
        """
        Generate Terraform 1.5+ import blocks.

        Returns:
            Terraform configuration with import blocks.
        """
        lines = [
            "# Terraform Import Blocks (Terraform 1.5+)",
            "# Run 'terraform plan -generate-config-out=generated.tf' to generate configuration",
            "",
        ]

        for imp in self.imports:
            lines.append(f'''import {{
  to = {imp["type"]}.{imp["name"]}
  id = "{imp["id"]}"
}}
''')

        return "\n".join(lines)

    def from_cloudformation_stack(
        self,
        stack_resources: List[Dict[str, Any]],
        resource_mapping: Dict[str, str],
    ) -> "ImportGenerator":
        """
        Generate imports from CloudFormation stack resources.

        Args:
            stack_resources: List of CF stack resources.
            resource_mapping: CF to Terraform type mapping.

        Returns:
            Self for method chaining.
        """
        for resource in stack_resources:
            cf_type = resource.get("ResourceType", "")
            logical_id = resource.get("LogicalResourceId", "")
            physical_id = resource.get("PhysicalResourceId", "")

            if cf_type in resource_mapping and physical_id:
                tf_type = resource_mapping[cf_type]
                tf_name = self._to_snake_case(logical_id)
                self.add_import(tf_type, tf_name, physical_id)

        return self

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


# Provider configuration templates
PROVIDER_CONFIGURATIONS = {
    "aws": '''terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = var.repository_url
    }
  }
}

# Secondary region provider (for DR/replication)
provider "aws" {
  alias  = "secondary"
  region = var.aws_secondary_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = var.repository_url
    }
  }
}
''',

    "aws_with_databricks": '''terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

provider "databricks" {
  alias = "mws"
  host  = "https://accounts.cloud.databricks.com"
  # Authentication via environment variables:
  # DATABRICKS_ACCOUNT_ID
  # DATABRICKS_CLIENT_ID
  # DATABRICKS_CLIENT_SECRET
}

provider "databricks" {
  alias = "workspace"
  host  = var.databricks_workspace_url
  # Uses AWS IAM authentication
}
''',
}
