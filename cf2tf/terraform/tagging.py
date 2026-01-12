"""
AWS Tagging Strategy Module

Implements enterprise tagging standards for cost allocation, compliance,
and resource management. Based on AWS Well-Architected Framework.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class TaggingStrategy:
    """Enterprise tagging strategy implementation."""

    # Standard tag keys (AWS recommended)
    STANDARD_TAGS = {
        "cost_allocation": [
            "Project",
            "Environment",
            "CostCenter",
            "Owner",
            "Application",
        ],
        "operations": [
            "ManagedBy",
            "CreatedBy",
            "CreatedDate",
            "UpdatedDate",
            "AutoShutdown",
            "BackupPolicy",
        ],
        "security": [
            "DataClassification",
            "Compliance",
            "SecurityZone",
        ],
        "automation": [
            "AutoScale",
            "PatchGroup",
            "MaintenanceWindow",
        ],
    }

    # Data classification levels
    DATA_CLASSIFICATIONS = [
        "public",
        "internal",
        "confidential",
        "restricted",
    ]

    # Compliance frameworks
    COMPLIANCE_FRAMEWORKS = [
        "soc2",
        "hipaa",
        "pci-dss",
        "gdpr",
        "fedramp",
        "iso27001",
    ]

    def __init__(
        self,
        project_name: str,
        environment: str,
        owner: str,
        cost_center: Optional[str] = None,
    ):
        """
        Initialize the TaggingStrategy.

        Args:
            project_name: Name of the project.
            environment: Deployment environment.
            owner: Team or person responsible.
            cost_center: Cost allocation center.
        """
        self.project_name = project_name
        self.environment = environment
        self.owner = owner
        self.cost_center = cost_center or "default"

    def get_base_tags(self) -> Dict[str, str]:
        """
        Get base tags required for all resources.

        Returns:
            Dictionary of base tags.
        """
        return {
            "Project": self.project_name,
            "Environment": self.environment,
            "Owner": self.owner,
            "CostCenter": self.cost_center,
            "ManagedBy": "terraform",
            "CreatedDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }

    def get_resource_tags(
        self,
        resource_name: str,
        resource_type: str,
        additional_tags: Optional[Dict[str, str]] = None,
        data_classification: str = "internal",
        compliance: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Get complete tags for a resource.

        Args:
            resource_name: Name of the resource.
            resource_type: Type of resource (e.g., "ec2", "rds").
            additional_tags: Additional custom tags.
            data_classification: Data classification level.
            compliance: List of compliance frameworks.

        Returns:
            Complete tag dictionary.
        """
        tags = self.get_base_tags()
        tags["Name"] = f"{self.project_name}-{self.environment}-{resource_name}"
        tags["ResourceType"] = resource_type
        tags["DataClassification"] = data_classification

        if compliance:
            tags["Compliance"] = ",".join(compliance)

        if additional_tags:
            tags.update(additional_tags)

        return tags

    def generate_terraform_locals(self) -> str:
        """
        Generate Terraform locals block for tags.

        Returns:
            Terraform configuration string.
        """
        return f'''# ==============================================================================
# Tagging Strategy - Enterprise Standards
# ==============================================================================

locals {{
  # Base tags applied to all resources
  base_tags = {{
    Project      = var.project_name
    Environment  = var.environment
    Owner        = var.owner
    CostCenter   = var.cost_center
    ManagedBy    = "terraform"
    Repository   = var.repository_url
    CreatedDate  = timestamp()
  }}

  # Environment-specific tags
  env_tags = {{
    dev = {{
      AutoShutdown = "true"
      BackupPolicy = "daily-7"
    }}
    staging = {{
      AutoShutdown = "false"
      BackupPolicy = "daily-14"
    }}
    prod = {{
      AutoShutdown = "false"
      BackupPolicy = "daily-30"
      Compliance   = "soc2,pci-dss"
    }}
  }}

  # Data classification tags
  data_classification_tags = {{
    public = {{
      DataClassification = "public"
      Encryption         = "optional"
    }}
    internal = {{
      DataClassification = "internal"
      Encryption         = "required"
    }}
    confidential = {{
      DataClassification = "confidential"
      Encryption         = "required"
      AccessControl      = "restricted"
    }}
    restricted = {{
      DataClassification = "restricted"
      Encryption         = "required"
      AccessControl      = "strict"
      AuditLog           = "required"
    }}
  }}

  # Merge all tags
  common_tags = merge(
    local.base_tags,
    lookup(local.env_tags, var.environment, {{}})
  )
}}

# Variables for tagging
variable "project_name" {{
  description = "Name of the project"
  type        = string
}}

variable "environment" {{
  description = "Deployment environment (dev, staging, prod)"
  type        = string

  validation {{
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }}
}}

variable "owner" {{
  description = "Team or person responsible for the resources"
  type        = string
}}

variable "cost_center" {{
  description = "Cost allocation center"
  type        = string
  default     = "engineering"
}}

variable "repository_url" {{
  description = "URL of the source code repository"
  type        = string
  default     = ""
}}

# Helper function for resource naming
locals {{
  name_prefix = "${{var.project_name}}-${{var.environment}}"

  # Standard naming convention: project-env-resource-identifier
  resource_name = {{
    vpc        = "${{local.name_prefix}}-vpc"
    subnet     = "${{local.name_prefix}}-subnet"
    sg         = "${{local.name_prefix}}-sg"
    ec2        = "${{local.name_prefix}}-ec2"
    rds        = "${{local.name_prefix}}-rds"
    s3         = "${{var.project_name}}-${{var.environment}}"  # S3 doesn't allow uppercase
    lambda     = "${{local.name_prefix}}-lambda"
    ecs        = "${{local.name_prefix}}-ecs"
    eks        = "${{local.name_prefix}}-eks"
  }}
}}

# Usage example:
# resource "aws_instance" "app" {{
#   tags = merge(local.common_tags, {{
#     Name = "${{local.resource_name.ec2}}-app"
#     Role = "application-server"
#   }})
# }}
'''

    def generate_aws_config_rules(self) -> str:
        """
        Generate AWS Config rules for tag compliance.

        Returns:
            Terraform configuration for Config rules.
        """
        return '''# ==============================================================================
# AWS Config Rules for Tag Compliance
# ==============================================================================

resource "aws_config_config_rule" "required_tags" {
  name = "${var.project_name}-required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key   = "Project"
    tag2Key   = "Environment"
    tag3Key   = "Owner"
    tag4Key   = "CostCenter"
    tag5Key   = "ManagedBy"
  })

  scope {
    compliance_resource_types = [
      "AWS::EC2::Instance",
      "AWS::EC2::SecurityGroup",
      "AWS::EC2::Volume",
      "AWS::RDS::DBInstance",
      "AWS::S3::Bucket",
      "AWS::Lambda::Function",
      "AWS::ECS::Cluster",
      "AWS::EKS::Cluster",
    ]
  }

  tags = local.common_tags
}

resource "aws_config_config_rule" "data_classification_tag" {
  name = "${var.project_name}-data-classification-tag"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key   = "DataClassification"
    tag1Value = "public,internal,confidential,restricted"
  })

  scope {
    compliance_resource_types = [
      "AWS::S3::Bucket",
      "AWS::RDS::DBInstance",
      "AWS::DynamoDB::Table",
      "AWS::EFS::FileSystem",
    ]
  }

  tags = local.common_tags
}

# Auto-remediation for missing tags (optional)
resource "aws_config_remediation_configuration" "required_tags" {
  config_rule_name = aws_config_config_rule.required_tags.name
  target_type      = "SSM_DOCUMENT"
  target_id        = "AWS-SetRequiredTags"

  parameter {
    name         = "RequiredTags"
    static_value = jsonencode(local.common_tags)
  }

  automatic                  = false  # Set to true for auto-remediation
  maximum_automatic_attempts = 3
  retry_attempt_seconds      = 60
}
'''

    def generate_cost_allocation_report(self) -> str:
        """
        Generate Cost and Usage Report configuration.

        Returns:
            Terraform configuration for CUR.
        """
        return '''# ==============================================================================
# AWS Cost and Usage Report Configuration
# ==============================================================================

resource "aws_cur_report_definition" "cost_report" {
  report_name                = "${var.project_name}-cost-report"
  time_unit                  = "DAILY"
  format                     = "Parquet"
  compression                = "Parquet"
  additional_schema_elements = ["RESOURCES", "SPLIT_COST_ALLOCATION_DATA"]
  s3_bucket                  = aws_s3_bucket.cost_reports.id
  s3_prefix                  = "cost-reports"
  s3_region                  = var.aws_region
  report_versioning          = "OVERWRITE_REPORT"

  additional_artifacts = ["ATHENA"]
}

resource "aws_s3_bucket" "cost_reports" {
  bucket = "${var.project_name}-cost-reports-${data.aws_caller_identity.current.account_id}"

  tags = merge(local.common_tags, {
    Name    = "${var.project_name}-cost-reports"
    Purpose = "cost-allocation"
  })
}

resource "aws_s3_bucket_policy" "cost_reports" {
  bucket = aws_s3_bucket.cost_reports.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCURWrite"
        Effect    = "Allow"
        Principal = {
          Service = "billingreports.amazonaws.com"
        }
        Action = [
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy",
          "s3:PutObject"
        ]
        Resource = [
          aws_s3_bucket.cost_reports.arn,
          "${aws_s3_bucket.cost_reports.arn}/*"
        ]
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# Activate cost allocation tags
resource "aws_ce_cost_allocation_tag" "project" {
  tag_key = "Project"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "environment" {
  tag_key = "Environment"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "cost_center" {
  tag_key = "CostCenter"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "owner" {
  tag_key = "Owner"
  status  = "Active"
}
'''
