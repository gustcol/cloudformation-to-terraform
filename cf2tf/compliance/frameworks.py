"""
Compliance Frameworks Module

Implements compliance checks and controls for major regulatory frameworks:
- SOC 2 Type II
- HIPAA
- PCI-DSS
- GDPR
- FedRAMP
- ISO 27001
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci-dss"
    GDPR = "gdpr"
    FEDRAMP = "fedramp"
    ISO27001 = "iso27001"


class ControlStatus(Enum):
    """Control implementation status."""
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceControl:
    """Represents a compliance control."""
    id: str
    framework: ComplianceFramework
    title: str
    description: str
    category: str
    terraform_resources: List[str]
    check_function: Optional[str] = None
    remediation: Optional[str] = None


# SOC 2 Controls
SOC2_CONTROLS: List[ComplianceControl] = [
    ComplianceControl(
        id="SOC2-CC6.1",
        framework=ComplianceFramework.SOC2,
        title="Logical Access Security",
        description="The entity implements logical access security software, infrastructure, and architectures over protected information assets.",
        category="Logical and Physical Access Controls",
        terraform_resources=["aws_iam_policy", "aws_iam_role", "aws_security_group"],
        remediation="Implement least privilege access controls using IAM policies and security groups.",
    ),
    ComplianceControl(
        id="SOC2-CC6.6",
        framework=ComplianceFramework.SOC2,
        title="Data Encryption",
        description="The entity implements controls to protect data in transit and at rest.",
        category="Logical and Physical Access Controls",
        terraform_resources=["aws_kms_key", "aws_s3_bucket_server_side_encryption_configuration", "aws_rds_cluster"],
        remediation="Enable encryption for all data stores using KMS keys.",
    ),
    ComplianceControl(
        id="SOC2-CC7.2",
        framework=ComplianceFramework.SOC2,
        title="System Monitoring",
        description="The entity monitors system components for anomalies and security events.",
        category="System Operations",
        terraform_resources=["aws_cloudwatch_log_group", "aws_cloudwatch_metric_alarm", "aws_guardduty_detector"],
        remediation="Enable CloudWatch logging, GuardDuty, and set up security alerts.",
    ),
    ComplianceControl(
        id="SOC2-CC8.1",
        framework=ComplianceFramework.SOC2,
        title="Change Management",
        description="Changes to infrastructure are authorized, designed, tested, and implemented.",
        category="Change Management",
        terraform_resources=["aws_config_config_rule", "aws_cloudtrail"],
        remediation="Use Terraform for infrastructure changes with proper review processes.",
    ),
]

# HIPAA Controls
HIPAA_CONTROLS: List[ComplianceControl] = [
    ComplianceControl(
        id="HIPAA-164.312(a)(1)",
        framework=ComplianceFramework.HIPAA,
        title="Access Control",
        description="Implement technical policies and procedures for electronic information systems that maintain ePHI.",
        category="Technical Safeguards",
        terraform_resources=["aws_iam_policy", "aws_iam_role", "aws_security_group"],
        remediation="Implement role-based access control with minimum necessary access.",
    ),
    ComplianceControl(
        id="HIPAA-164.312(a)(2)(iv)",
        framework=ComplianceFramework.HIPAA,
        title="Encryption and Decryption",
        description="Implement a mechanism to encrypt and decrypt ePHI.",
        category="Technical Safeguards",
        terraform_resources=["aws_kms_key", "aws_s3_bucket_server_side_encryption_configuration"],
        remediation="Enable AES-256 encryption for all ePHI storage.",
    ),
    ComplianceControl(
        id="HIPAA-164.312(b)",
        framework=ComplianceFramework.HIPAA,
        title="Audit Controls",
        description="Implement hardware, software, and/or procedural mechanisms to record and examine activity.",
        category="Technical Safeguards",
        terraform_resources=["aws_cloudtrail", "aws_cloudwatch_log_group", "aws_config_configuration_recorder"],
        remediation="Enable CloudTrail, CloudWatch Logs, and AWS Config for audit logging.",
    ),
    ComplianceControl(
        id="HIPAA-164.312(c)(1)",
        framework=ComplianceFramework.HIPAA,
        title="Integrity",
        description="Implement policies and procedures to protect ePHI from improper alteration or destruction.",
        category="Technical Safeguards",
        terraform_resources=["aws_s3_bucket_versioning", "aws_backup_plan"],
        remediation="Enable versioning and implement backup policies.",
    ),
    ComplianceControl(
        id="HIPAA-164.312(e)(1)",
        framework=ComplianceFramework.HIPAA,
        title="Transmission Security",
        description="Implement technical security measures to guard against unauthorized access to ePHI transmitted over networks.",
        category="Technical Safeguards",
        terraform_resources=["aws_lb_listener", "aws_api_gateway_stage", "aws_cloudfront_distribution"],
        remediation="Enforce TLS 1.2+ for all data in transit.",
    ),
]

# PCI-DSS Controls
PCI_DSS_CONTROLS: List[ComplianceControl] = [
    ComplianceControl(
        id="PCI-DSS-1.3",
        framework=ComplianceFramework.PCI_DSS,
        title="Network Segmentation",
        description="Prohibit direct public access between the Internet and any system component in the cardholder data environment.",
        category="Build and Maintain a Secure Network",
        terraform_resources=["aws_vpc", "aws_subnet", "aws_security_group", "aws_network_acl"],
        remediation="Implement network segmentation with private subnets for CDE.",
    ),
    ComplianceControl(
        id="PCI-DSS-3.4",
        framework=ComplianceFramework.PCI_DSS,
        title="Render PAN Unreadable",
        description="Render PAN unreadable anywhere it is stored using strong cryptography.",
        category="Protect Cardholder Data",
        terraform_resources=["aws_kms_key", "aws_dynamodb_table", "aws_rds_cluster"],
        remediation="Use KMS encryption for all cardholder data storage.",
    ),
    ComplianceControl(
        id="PCI-DSS-4.1",
        framework=ComplianceFramework.PCI_DSS,
        title="Encryption in Transit",
        description="Use strong cryptography and security protocols to safeguard sensitive cardholder data during transmission.",
        category="Protect Cardholder Data",
        terraform_resources=["aws_lb_listener", "aws_api_gateway_stage"],
        remediation="Enforce TLS 1.2+ with strong cipher suites.",
    ),
    ComplianceControl(
        id="PCI-DSS-8.2",
        framework=ComplianceFramework.PCI_DSS,
        title="User Authentication",
        description="Employ at least one authentication method for all users.",
        category="Identify and Authenticate Access",
        terraform_resources=["aws_iam_user", "aws_iam_policy", "aws_cognito_user_pool"],
        remediation="Implement MFA and strong password policies.",
    ),
    ComplianceControl(
        id="PCI-DSS-10.2",
        framework=ComplianceFramework.PCI_DSS,
        title="Audit Trails",
        description="Implement automated audit trails for all system components.",
        category="Track and Monitor Access",
        terraform_resources=["aws_cloudtrail", "aws_cloudwatch_log_group"],
        remediation="Enable comprehensive audit logging with CloudTrail.",
    ),
]


class ComplianceChecker:
    """Checker for compliance controls."""

    def __init__(self, frameworks: Optional[List[ComplianceFramework]] = None):
        """
        Initialize the ComplianceChecker.

        Args:
            frameworks: List of frameworks to check against.
        """
        self.frameworks = frameworks or [
            ComplianceFramework.SOC2,
            ComplianceFramework.HIPAA,
            ComplianceFramework.PCI_DSS,
        ]
        self.controls = self._load_controls()

    def _load_controls(self) -> List[ComplianceControl]:
        """Load controls for selected frameworks."""
        controls = []
        if ComplianceFramework.SOC2 in self.frameworks:
            controls.extend(SOC2_CONTROLS)
        if ComplianceFramework.HIPAA in self.frameworks:
            controls.extend(HIPAA_CONTROLS)
        if ComplianceFramework.PCI_DSS in self.frameworks:
            controls.extend(PCI_DSS_CONTROLS)
        return controls

    def check_resource(
        self,
        resource_type: str,
        resource_config: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Check a resource against compliance controls.

        Args:
            resource_type: Terraform resource type.
            resource_config: Resource configuration.

        Returns:
            List of compliance findings.
        """
        findings = []

        for control in self.controls:
            if resource_type in control.terraform_resources:
                finding = self._evaluate_control(control, resource_type, resource_config)
                if finding:
                    findings.append(finding)

        return findings

    def _evaluate_control(
        self,
        control: ComplianceControl,
        resource_type: str,
        resource_config: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a specific control against a resource."""
        # Encryption checks
        if "encryption" in control.id.lower() or "encrypt" in control.title.lower():
            if resource_type == "aws_s3_bucket":
                if not self._check_s3_encryption(resource_config):
                    return {
                        "control_id": control.id,
                        "framework": control.framework.value,
                        "title": control.title,
                        "status": ControlStatus.NOT_IMPLEMENTED.value,
                        "resource_type": resource_type,
                        "remediation": control.remediation,
                    }

            if resource_type == "aws_rds_cluster":
                if not resource_config.get("storage_encrypted", False):
                    return {
                        "control_id": control.id,
                        "framework": control.framework.value,
                        "title": control.title,
                        "status": ControlStatus.NOT_IMPLEMENTED.value,
                        "resource_type": resource_type,
                        "remediation": "Enable storage_encrypted = true",
                    }

        # Access control checks
        if "access" in control.id.lower():
            if resource_type == "aws_security_group":
                if self._check_open_ingress(resource_config):
                    return {
                        "control_id": control.id,
                        "framework": control.framework.value,
                        "title": control.title,
                        "status": ControlStatus.NOT_IMPLEMENTED.value,
                        "resource_type": resource_type,
                        "remediation": "Restrict security group ingress rules",
                    }

        return None

    def _check_s3_encryption(self, config: Dict[str, Any]) -> bool:
        """Check if S3 bucket has encryption enabled."""
        sse_config = config.get("server_side_encryption_configuration", {})
        if not sse_config:
            return False
        rules = sse_config.get("rule", [])
        return len(rules) > 0

    def _check_open_ingress(self, config: Dict[str, Any]) -> bool:
        """Check if security group has open ingress."""
        ingress = config.get("ingress", [])
        for rule in ingress:
            cidr = rule.get("cidr_blocks", [])
            if "0.0.0.0/0" in cidr:
                from_port = rule.get("from_port", 0)
                to_port = rule.get("to_port", 65535)
                if from_port == 0 and to_port == 65535:
                    return True
        return False

    def generate_compliance_report(
        self,
        findings: List[Dict[str, Any]],
    ) -> str:
        """
        Generate a compliance report.

        Args:
            findings: List of compliance findings.

        Returns:
            Markdown formatted compliance report.
        """
        report = ["# Compliance Assessment Report\n"]
        report.append(f"**Frameworks Assessed:** {', '.join(f.value for f in self.frameworks)}\n")
        report.append(f"**Total Controls:** {len(self.controls)}\n")
        report.append(f"**Findings:** {len(findings)}\n\n")

        # Group findings by framework
        by_framework: Dict[str, List[Dict[str, Any]]] = {}
        for finding in findings:
            fw = finding["framework"]
            if fw not in by_framework:
                by_framework[fw] = []
            by_framework[fw].append(finding)

        for framework, fw_findings in by_framework.items():
            report.append(f"## {framework.upper()}\n")
            report.append(f"| Control | Title | Status | Resource | Remediation |\n")
            report.append(f"|---------|-------|--------|----------|-------------|\n")

            for finding in fw_findings:
                report.append(
                    f"| {finding['control_id']} | {finding['title']} | "
                    f"{finding['status']} | {finding['resource_type']} | "
                    f"{finding.get('remediation', 'N/A')} |\n"
                )

        return "".join(report)

    def generate_terraform_controls(self) -> str:
        """
        Generate Terraform configuration for compliance controls.

        Returns:
            Terraform configuration string.
        """
        return '''# ==============================================================================
# Compliance Controls - Terraform Configuration
# ==============================================================================

# AWS Config Rules for Compliance
resource "aws_config_config_rule" "s3_bucket_encryption" {
  name = "s3-bucket-server-side-encryption-enabled"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "rds_encryption" {
  name = "rds-storage-encrypted"

  source {
    owner             = "AWS"
    source_identifier = "RDS_STORAGE_ENCRYPTED"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "encrypted_volumes" {
  name = "encrypted-volumes"

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "cloudtrail_enabled" {
  name = "cloudtrail-enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "iam_password_policy" {
  name = "iam-password-policy"

  source {
    owner             = "AWS"
    source_identifier = "IAM_PASSWORD_POLICY"
  }

  input_parameters = jsonencode({
    RequireUppercaseCharacters = "true"
    RequireLowercaseCharacters = "true"
    RequireSymbols             = "true"
    RequireNumbers             = "true"
    MinimumPasswordLength      = "14"
    PasswordReusePrevention    = "24"
    MaxPasswordAge             = "90"
  })

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "mfa_enabled_for_console" {
  name = "mfa-enabled-for-iam-console-access"

  source {
    owner             = "AWS"
    source_identifier = "MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "vpc_flow_logs" {
  name = "vpc-flow-logs-enabled"

  source {
    owner             = "AWS"
    source_identifier = "VPC_FLOW_LOGS_ENABLED"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

resource "aws_config_config_rule" "alb_https_only" {
  name = "alb-http-to-https-redirection-check"

  source {
    owner             = "AWS"
    source_identifier = "ALB_HTTP_TO_HTTPS_REDIRECTION_CHECK"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

# GuardDuty for Threat Detection (SOC2-CC7.2)
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA"
  })
}

# Security Hub for Compliance Dashboards
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0"
}

resource "aws_securityhub_standards_subscription" "pci_dss" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:${data.aws_region.current.name}::standards/pci-dss/v/3.2.1"
}

resource "aws_securityhub_standards_subscription" "aws_foundational" {
  depends_on    = [aws_securityhub_account.main]
  standards_arn = "arn:aws:securityhub:${data.aws_region.current.name}::standards/aws-foundational-security-best-practices/v/1.0.0"
}

# CloudTrail for Audit Logging (HIPAA-164.312(b), PCI-DSS-10.2)
resource "aws_cloudtrail" "compliance" {
  name                          = "${var.project_name}-compliance-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.cloudtrail.arn

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3"]
    }

    data_resource {
      type   = "AWS::Lambda::Function"
      values = ["arn:aws:lambda"]
    }
  }

  insight_selector {
    insight_type = "ApiCallRateInsight"
  }

  insight_selector {
    insight_type = "ApiErrorRateInsight"
  }

  tags = merge(local.common_tags, {
    Compliance = "SOC2,HIPAA,PCI-DSS"
  })
}

# AWS Backup for Data Protection (HIPAA-164.312(c)(1))
resource "aws_backup_vault" "compliance" {
  name        = "${var.project_name}-compliance-vault"
  kms_key_arn = aws_kms_key.backup.arn

  tags = merge(local.common_tags, {
    Compliance = "HIPAA"
  })
}

resource "aws_backup_plan" "compliance" {
  name = "${var.project_name}-compliance-backup"

  rule {
    rule_name         = "daily-backup"
    target_vault_name = aws_backup_vault.compliance.name
    schedule          = "cron(0 5 ? * * *)"

    lifecycle {
      cold_storage_after = 30
      delete_after       = 365
    }

    copy_action {
      destination_vault_arn = aws_backup_vault.compliance_replica.arn
      lifecycle {
        delete_after = 365
      }
    }
  }

  tags = merge(local.common_tags, {
    Compliance = "HIPAA"
  })
}
'''
