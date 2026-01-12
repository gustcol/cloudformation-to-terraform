"""
Security Rules based on Checkov and AWS Best Practices

This module contains security rules that are checked against CloudFormation
resources during conversion. Rules are categorized by AWS service and severity.
"""

from typing import Any, Callable, Dict, List, Optional

# Rule structure:
# {
#     "id": "CKV_AWS_XXX",  # Checkov-style ID
#     "title": "Human readable title",
#     "description": "Detailed description of the security issue",
#     "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
#     "resource_types": ["AWS::Service::Resource"],
#     "check": callable(resource_properties) -> bool,  # Returns True if violation found
#     "recommendation": "How to fix",
#     "terraform_fix": "Example Terraform code to fix the issue",
#     "references": ["URL to documentation"],
# }


def check_s3_public_access(properties: Dict[str, Any]) -> bool:
    """Check if S3 bucket allows public access."""
    acl = properties.get("AccessControl", "")
    if acl in ["PublicRead", "PublicReadWrite", "AuthenticatedRead"]:
        return True

    # Check PublicAccessBlockConfiguration
    public_block = properties.get("PublicAccessBlockConfiguration", {})
    if not public_block:
        return True

    required_blocks = [
        "BlockPublicAcls",
        "BlockPublicPolicy",
        "IgnorePublicAcls",
        "RestrictPublicBuckets",
    ]
    return not all(public_block.get(block, False) for block in required_blocks)


def check_s3_encryption(properties: Dict[str, Any]) -> bool:
    """Check if S3 bucket has encryption enabled."""
    encryption = properties.get("BucketEncryption", {})
    rules = encryption.get("ServerSideEncryptionConfiguration", [])
    return not bool(rules)


def check_s3_versioning(properties: Dict[str, Any]) -> bool:
    """Check if S3 bucket has versioning enabled."""
    versioning = properties.get("VersioningConfiguration", {})
    return versioning.get("Status") != "Enabled"


def check_s3_logging(properties: Dict[str, Any]) -> bool:
    """Check if S3 bucket has logging enabled."""
    logging = properties.get("LoggingConfiguration", {})
    return not bool(logging.get("DestinationBucketName"))


def check_ec2_imdsv2(properties: Dict[str, Any]) -> bool:
    """Check if EC2 instance requires IMDSv2."""
    metadata_options = properties.get("MetadataOptions", {})
    return metadata_options.get("HttpTokens") != "required"


def check_ec2_public_ip(properties: Dict[str, Any]) -> bool:
    """Check if EC2 instance has public IP disabled."""
    network_interfaces = properties.get("NetworkInterfaces", [])
    for ni in network_interfaces:
        if ni.get("AssociatePublicIpAddress", False):
            return True
    return False


def check_ec2_ebs_encryption(properties: Dict[str, Any]) -> bool:
    """Check if EC2 instance EBS volumes are encrypted."""
    block_devices = properties.get("BlockDeviceMappings", [])
    for device in block_devices:
        ebs = device.get("Ebs", {})
        if ebs and not ebs.get("Encrypted", False):
            return True
    return False


def check_sg_unrestricted_ingress(properties: Dict[str, Any]) -> bool:
    """Check for unrestricted ingress rules (0.0.0.0/0)."""
    ingress = properties.get("SecurityGroupIngress", [])
    for rule in ingress:
        cidr = rule.get("CidrIp", "")
        if cidr in ["0.0.0.0/0", "::/0"]:
            from_port = rule.get("FromPort", 0)
            to_port = rule.get("ToPort", 65535)
            # Check for wide-open ports (not just HTTP/HTTPS)
            if from_port not in [80, 443] or to_port not in [80, 443]:
                return True
    return False


def check_sg_ssh_open(properties: Dict[str, Any]) -> bool:
    """Check if SSH (port 22) is open to the world."""
    ingress = properties.get("SecurityGroupIngress", [])
    for rule in ingress:
        cidr = rule.get("CidrIp", "")
        if cidr in ["0.0.0.0/0", "::/0"]:
            from_port = rule.get("FromPort", 0)
            to_port = rule.get("ToPort", 65535)
            if from_port <= 22 <= to_port:
                return True
    return False


def check_sg_rdp_open(properties: Dict[str, Any]) -> bool:
    """Check if RDP (port 3389) is open to the world."""
    ingress = properties.get("SecurityGroupIngress", [])
    for rule in ingress:
        cidr = rule.get("CidrIp", "")
        if cidr in ["0.0.0.0/0", "::/0"]:
            from_port = rule.get("FromPort", 0)
            to_port = rule.get("ToPort", 65535)
            if from_port <= 3389 <= to_port:
                return True
    return False


def check_rds_encryption(properties: Dict[str, Any]) -> bool:
    """Check if RDS instance has encryption enabled."""
    return not properties.get("StorageEncrypted", False)


def check_rds_public(properties: Dict[str, Any]) -> bool:
    """Check if RDS instance is publicly accessible."""
    return properties.get("PubliclyAccessible", False)


def check_rds_backup(properties: Dict[str, Any]) -> bool:
    """Check if RDS instance has adequate backup retention."""
    retention = properties.get("BackupRetentionPeriod", 0)
    return retention < 7


def check_rds_multi_az(properties: Dict[str, Any]) -> bool:
    """Check if RDS instance has Multi-AZ enabled."""
    return not properties.get("MultiAZ", False)


def check_rds_deletion_protection(properties: Dict[str, Any]) -> bool:
    """Check if RDS instance has deletion protection enabled."""
    return not properties.get("DeletionProtection", False)


def check_iam_wildcard_action(properties: Dict[str, Any]) -> bool:
    """Check for IAM policies with wildcard actions."""
    policy = properties.get("PolicyDocument", {})
    statements = policy.get("Statement", [])
    for stmt in statements:
        actions = stmt.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        if "*" in actions or any(a.endswith(":*") for a in actions):
            return True
    return False


def check_iam_wildcard_resource(properties: Dict[str, Any]) -> bool:
    """Check for IAM policies with wildcard resources."""
    policy = properties.get("PolicyDocument", {})
    statements = policy.get("Statement", [])
    for stmt in statements:
        resources = stmt.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]
        if "*" in resources:
            return True
    return False


def check_iam_admin_policy(properties: Dict[str, Any]) -> bool:
    """Check for IAM policies that grant admin access."""
    policy = properties.get("PolicyDocument", {})
    statements = policy.get("Statement", [])
    for stmt in statements:
        effect = stmt.get("Effect", "")
        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])
        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]
        if effect == "Allow" and "*" in actions and "*" in resources:
            return True
    return False


def check_lambda_tracing(properties: Dict[str, Any]) -> bool:
    """Check if Lambda function has X-Ray tracing enabled."""
    tracing = properties.get("TracingConfig", {})
    return tracing.get("Mode") != "Active"


def check_lambda_vpc(properties: Dict[str, Any]) -> bool:
    """Check if Lambda function is configured with VPC."""
    vpc_config = properties.get("VpcConfig", {})
    return not bool(vpc_config.get("SubnetIds"))


def check_dynamodb_encryption(properties: Dict[str, Any]) -> bool:
    """Check if DynamoDB table has encryption enabled."""
    sse = properties.get("SSESpecification", {})
    return not sse.get("SSEEnabled", False)


def check_dynamodb_pitr(properties: Dict[str, Any]) -> bool:
    """Check if DynamoDB table has Point-in-Time Recovery enabled."""
    pitr = properties.get("PointInTimeRecoverySpecification", {})
    return not pitr.get("PointInTimeRecoveryEnabled", False)


def check_kms_rotation(properties: Dict[str, Any]) -> bool:
    """Check if KMS key has rotation enabled."""
    return not properties.get("EnableKeyRotation", False)


def check_sns_encryption(properties: Dict[str, Any]) -> bool:
    """Check if SNS topic has encryption enabled."""
    return not properties.get("KmsMasterKeyId")


def check_sqs_encryption(properties: Dict[str, Any]) -> bool:
    """Check if SQS queue has encryption enabled."""
    return not properties.get("KmsMasterKeyId")


def check_elb_logging(properties: Dict[str, Any]) -> bool:
    """Check if ELB/ALB has access logging enabled."""
    attributes = properties.get("LoadBalancerAttributes", [])
    for attr in attributes:
        if attr.get("Key") == "access_logs.s3.enabled":
            return attr.get("Value") != "true"
    return True


def check_elb_https(properties: Dict[str, Any]) -> bool:
    """Check if ELB/ALB uses HTTPS listeners."""
    # This check is context-dependent, return False as default
    return False


def check_cloudwatch_log_encryption(properties: Dict[str, Any]) -> bool:
    """Check if CloudWatch Log Group has encryption enabled."""
    return not properties.get("KmsKeyId")


def check_ecs_container_insights(properties: Dict[str, Any]) -> bool:
    """Check if ECS cluster has Container Insights enabled."""
    settings = properties.get("ClusterSettings", [])
    for setting in settings:
        if setting.get("Name") == "containerInsights":
            return setting.get("Value") != "enabled"
    return True


def check_ecr_scan_on_push(properties: Dict[str, Any]) -> bool:
    """Check if ECR repository has scan on push enabled."""
    scan_config = properties.get("ImageScanningConfiguration", {})
    return not scan_config.get("ScanOnPush", False)


def check_ecr_immutable_tags(properties: Dict[str, Any]) -> bool:
    """Check if ECR repository has immutable tags."""
    return properties.get("ImageTagMutability", "MUTABLE") != "IMMUTABLE"


def check_vpc_flow_logs(properties: Dict[str, Any]) -> bool:
    """Check if VPC has flow logs enabled (checked via separate resource)."""
    # This would need cross-resource checking
    return False


def check_api_gateway_logging(properties: Dict[str, Any]) -> bool:
    """Check if API Gateway has logging enabled."""
    # Stage-level check
    return not properties.get("TracingEnabled", False)


# All security rules organized by service
SECURITY_RULES: List[Dict[str, Any]] = [
    # S3 Rules
    {
        "id": "CKV_AWS_18",
        "title": "S3 Bucket Public Access",
        "description": "S3 bucket should not allow public access. Public buckets can expose sensitive data to unauthorized users.",
        "severity": "CRITICAL",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_public_access,
        "recommendation": "Enable public access block configuration and set all options to true.",
        "terraform_fix": '''resource "aws_s3_bucket_public_access_block" "example" {
  bucket = aws_s3_bucket.example.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}''',
        "references": ["https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html"],
    },
    {
        "id": "CKV_AWS_19",
        "title": "S3 Bucket Encryption",
        "description": "S3 bucket should have server-side encryption enabled to protect data at rest.",
        "severity": "HIGH",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_encryption,
        "recommendation": "Enable server-side encryption using AWS KMS or AES-256.",
        "terraform_fix": '''resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.mykey.arn
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html"],
    },
    {
        "id": "CKV_AWS_21",
        "title": "S3 Bucket Versioning",
        "description": "S3 bucket should have versioning enabled to protect against accidental deletion.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_versioning,
        "recommendation": "Enable versioning on the S3 bucket.",
        "terraform_fix": '''resource "aws_s3_bucket_versioning" "example" {
  bucket = aws_s3_bucket.example.id
  versioning_configuration {
    status = "Enabled"
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html"],
    },
    {
        "id": "CKV_AWS_18",
        "title": "S3 Bucket Logging",
        "description": "S3 bucket should have access logging enabled for audit and compliance purposes.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_logging,
        "recommendation": "Enable access logging and specify a target bucket.",
        "terraform_fix": '''resource "aws_s3_bucket_logging" "example" {
  bucket = aws_s3_bucket.example.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}''',
        "references": ["https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html"],
    },
    # EC2 Rules
    {
        "id": "CKV_AWS_79",
        "title": "EC2 IMDSv2 Required",
        "description": "EC2 instance should require IMDSv2 to prevent SSRF attacks on metadata service.",
        "severity": "HIGH",
        "resource_types": ["AWS::EC2::Instance", "AWS::EC2::LaunchTemplate"],
        "check": check_ec2_imdsv2,
        "recommendation": "Configure metadata options to require IMDSv2 (HttpTokens = required).",
        "terraform_fix": '''resource "aws_instance" "example" {
  # ... other configuration ...

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
}''',
        "references": ["https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html"],
    },
    {
        "id": "CKV_AWS_88",
        "title": "EC2 Public IP Disabled",
        "description": "EC2 instances should not have public IP addresses unless necessary.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::EC2::Instance"],
        "check": check_ec2_public_ip,
        "recommendation": "Disable public IP assignment and use NAT Gateway or VPN for internet access.",
        "terraform_fix": '''resource "aws_instance" "example" {
  # ... other configuration ...

  associate_public_ip_address = false
}''',
        "references": ["https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html"],
    },
    {
        "id": "CKV_AWS_3",
        "title": "EC2 EBS Encryption",
        "description": "EC2 instance EBS volumes should be encrypted to protect data at rest.",
        "severity": "HIGH",
        "resource_types": ["AWS::EC2::Instance", "AWS::EC2::Volume"],
        "check": check_ec2_ebs_encryption,
        "recommendation": "Enable encryption on all EBS volumes.",
        "terraform_fix": '''resource "aws_instance" "example" {
  # ... other configuration ...

  root_block_device {
    encrypted = true
  }

  ebs_block_device {
    device_name = "/dev/sdf"
    encrypted   = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html"],
    },
    # Security Group Rules
    {
        "id": "CKV_AWS_23",
        "title": "Security Group Unrestricted Ingress",
        "description": "Security group should not have unrestricted ingress rules (0.0.0.0/0) for non-standard ports.",
        "severity": "HIGH",
        "resource_types": ["AWS::EC2::SecurityGroup"],
        "check": check_sg_unrestricted_ingress,
        "recommendation": "Restrict ingress rules to specific IP ranges or security groups.",
        "terraform_fix": '''resource "aws_security_group" "example" {
  # ... other configuration ...

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Restrict to internal network
  }
}''',
        "references": ["https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"],
    },
    {
        "id": "CKV_AWS_24",
        "title": "Security Group SSH Open to World",
        "description": "Security group should not have SSH (port 22) open to 0.0.0.0/0.",
        "severity": "CRITICAL",
        "resource_types": ["AWS::EC2::SecurityGroup"],
        "check": check_sg_ssh_open,
        "recommendation": "Restrict SSH access to specific IP ranges or use AWS Systems Manager Session Manager.",
        "terraform_fix": '''resource "aws_security_group" "example" {
  # ... other configuration ...

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Restrict to internal network
    # Or use security_groups for VPN/bastion access
  }
}''',
        "references": ["https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"],
    },
    {
        "id": "CKV_AWS_25",
        "title": "Security Group RDP Open to World",
        "description": "Security group should not have RDP (port 3389) open to 0.0.0.0/0.",
        "severity": "CRITICAL",
        "resource_types": ["AWS::EC2::SecurityGroup"],
        "check": check_sg_rdp_open,
        "recommendation": "Restrict RDP access to specific IP ranges or use AWS Systems Manager.",
        "terraform_fix": '''resource "aws_security_group" "example" {
  # ... other configuration ...

  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Restrict to internal network
  }
}''',
        "references": ["https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html"],
    },
    # RDS Rules
    {
        "id": "CKV_AWS_16",
        "title": "RDS Encryption",
        "description": "RDS instance should have encryption enabled to protect data at rest.",
        "severity": "HIGH",
        "resource_types": ["AWS::RDS::DBInstance", "AWS::RDS::DBCluster"],
        "check": check_rds_encryption,
        "recommendation": "Enable storage encryption using AWS KMS.",
        "terraform_fix": '''resource "aws_db_instance" "example" {
  # ... other configuration ...

  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn
}''',
        "references": ["https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html"],
    },
    {
        "id": "CKV_AWS_17",
        "title": "RDS Public Access",
        "description": "RDS instance should not be publicly accessible.",
        "severity": "CRITICAL",
        "resource_types": ["AWS::RDS::DBInstance", "AWS::RDS::DBCluster"],
        "check": check_rds_public,
        "recommendation": "Disable public accessibility and use VPC security groups.",
        "terraform_fix": '''resource "aws_db_instance" "example" {
  # ... other configuration ...

  publicly_accessible = false
}''',
        "references": ["https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html"],
    },
    {
        "id": "CKV_AWS_133",
        "title": "RDS Backup Retention",
        "description": "RDS instance should have adequate backup retention period (at least 7 days).",
        "severity": "MEDIUM",
        "resource_types": ["AWS::RDS::DBInstance", "AWS::RDS::DBCluster"],
        "check": check_rds_backup,
        "recommendation": "Set backup retention period to at least 7 days.",
        "terraform_fix": '''resource "aws_db_instance" "example" {
  # ... other configuration ...

  backup_retention_period = 7
}''',
        "references": ["https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html"],
    },
    {
        "id": "CKV_AWS_157",
        "title": "RDS Multi-AZ",
        "description": "RDS instance should have Multi-AZ enabled for high availability.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::RDS::DBInstance"],
        "check": check_rds_multi_az,
        "recommendation": "Enable Multi-AZ deployment for production databases.",
        "terraform_fix": '''resource "aws_db_instance" "example" {
  # ... other configuration ...

  multi_az = true
}''',
        "references": ["https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html"],
    },
    {
        "id": "CKV_AWS_293",
        "title": "RDS Deletion Protection",
        "description": "RDS instance should have deletion protection enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::RDS::DBInstance", "AWS::RDS::DBCluster"],
        "check": check_rds_deletion_protection,
        "recommendation": "Enable deletion protection to prevent accidental deletion.",
        "terraform_fix": '''resource "aws_db_instance" "example" {
  # ... other configuration ...

  deletion_protection = true
}''',
        "references": ["https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_DeleteInstance.html"],
    },
    # IAM Rules
    {
        "id": "CKV_AWS_49",
        "title": "IAM Policy Wildcard Action",
        "description": "IAM policy should not use wildcard actions (*) which grants excessive permissions.",
        "severity": "HIGH",
        "resource_types": ["AWS::IAM::Policy", "AWS::IAM::ManagedPolicy", "AWS::IAM::Role"],
        "check": check_iam_wildcard_action,
        "recommendation": "Specify explicit actions following the principle of least privilege.",
        "terraform_fix": '''resource "aws_iam_policy" "example" {
  name = "example"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::my-bucket/*"
      }
    ]
  })
}''',
        "references": ["https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"],
    },
    {
        "id": "CKV_AWS_107",
        "title": "IAM Policy Wildcard Resource",
        "description": "IAM policy should not use wildcard resources (*) which grants access to all resources.",
        "severity": "HIGH",
        "resource_types": ["AWS::IAM::Policy", "AWS::IAM::ManagedPolicy", "AWS::IAM::Role"],
        "check": check_iam_wildcard_resource,
        "recommendation": "Specify explicit resource ARNs following the principle of least privilege.",
        "terraform_fix": '''resource "aws_iam_policy" "example" {
  name = "example"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "arn:aws:s3:::my-bucket/*"
      }
    ]
  })
}''',
        "references": ["https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"],
    },
    {
        "id": "CKV_AWS_62",
        "title": "IAM Admin Policy",
        "description": "IAM policy should not grant full administrator access (Action: *, Resource: *).",
        "severity": "CRITICAL",
        "resource_types": ["AWS::IAM::Policy", "AWS::IAM::ManagedPolicy", "AWS::IAM::Role"],
        "check": check_iam_admin_policy,
        "recommendation": "Follow the principle of least privilege and grant only necessary permissions.",
        "terraform_fix": '''# Use specific permissions instead of admin access
resource "aws_iam_policy" "example" {
  name = "example"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = "us-east-1"
          }
        }
      }
    ]
  })
}''',
        "references": ["https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"],
    },
    # Lambda Rules
    {
        "id": "CKV_AWS_50",
        "title": "Lambda X-Ray Tracing",
        "description": "Lambda function should have X-Ray tracing enabled for observability.",
        "severity": "LOW",
        "resource_types": ["AWS::Lambda::Function"],
        "check": check_lambda_tracing,
        "recommendation": "Enable X-Ray tracing in Active mode.",
        "terraform_fix": '''resource "aws_lambda_function" "example" {
  # ... other configuration ...

  tracing_config {
    mode = "Active"
  }
}''',
        "references": ["https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html"],
    },
    {
        "id": "CKV_AWS_117",
        "title": "Lambda VPC Configuration",
        "description": "Lambda function should be deployed in a VPC for network isolation.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Lambda::Function"],
        "check": check_lambda_vpc,
        "recommendation": "Configure VPC settings with appropriate subnets and security groups.",
        "terraform_fix": '''resource "aws_lambda_function" "example" {
  # ... other configuration ...

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }
}''',
        "references": ["https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html"],
    },
    # DynamoDB Rules
    {
        "id": "CKV_AWS_28",
        "title": "DynamoDB Encryption",
        "description": "DynamoDB table should have encryption enabled using AWS managed or customer managed KMS key.",
        "severity": "HIGH",
        "resource_types": ["AWS::DynamoDB::Table"],
        "check": check_dynamodb_encryption,
        "recommendation": "Enable server-side encryption with KMS.",
        "terraform_fix": '''resource "aws_dynamodb_table" "example" {
  # ... other configuration ...

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
}''',
        "references": ["https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/EncryptionAtRest.html"],
    },
    {
        "id": "CKV_AWS_35",
        "title": "DynamoDB Point-in-Time Recovery",
        "description": "DynamoDB table should have Point-in-Time Recovery (PITR) enabled for data protection.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::DynamoDB::Table"],
        "check": check_dynamodb_pitr,
        "recommendation": "Enable Point-in-Time Recovery for the table.",
        "terraform_fix": '''resource "aws_dynamodb_table" "example" {
  # ... other configuration ...

  point_in_time_recovery {
    enabled = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html"],
    },
    # KMS Rules
    {
        "id": "CKV_AWS_7",
        "title": "KMS Key Rotation",
        "description": "KMS key should have automatic rotation enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::KMS::Key"],
        "check": check_kms_rotation,
        "recommendation": "Enable automatic key rotation for symmetric KMS keys.",
        "terraform_fix": '''resource "aws_kms_key" "example" {
  description         = "Example KMS key"
  enable_key_rotation = true
}''',
        "references": ["https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html"],
    },
    # SNS Rules
    {
        "id": "CKV_AWS_26",
        "title": "SNS Topic Encryption",
        "description": "SNS topic should have encryption enabled using KMS.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::SNS::Topic"],
        "check": check_sns_encryption,
        "recommendation": "Enable server-side encryption with KMS.",
        "terraform_fix": '''resource "aws_sns_topic" "example" {
  name              = "example"
  kms_master_key_id = aws_kms_key.sns.id
}''',
        "references": ["https://docs.aws.amazon.com/sns/latest/dg/sns-server-side-encryption.html"],
    },
    # SQS Rules
    {
        "id": "CKV_AWS_27",
        "title": "SQS Queue Encryption",
        "description": "SQS queue should have encryption enabled using KMS.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::SQS::Queue"],
        "check": check_sqs_encryption,
        "recommendation": "Enable server-side encryption with KMS.",
        "terraform_fix": '''resource "aws_sqs_queue" "example" {
  name              = "example"
  kms_master_key_id = aws_kms_key.sqs.id
}''',
        "references": ["https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-server-side-encryption.html"],
    },
    # ELB Rules
    {
        "id": "CKV_AWS_92",
        "title": "ELB Access Logging",
        "description": "ELB/ALB should have access logging enabled for audit and troubleshooting.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ElasticLoadBalancingV2::LoadBalancer", "AWS::ElasticLoadBalancing::LoadBalancer"],
        "check": check_elb_logging,
        "recommendation": "Enable access logging and specify an S3 bucket.",
        "terraform_fix": '''resource "aws_lb" "example" {
  # ... other configuration ...

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    prefix  = "lb-logs"
    enabled = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html"],
    },
    # CloudWatch Logs Rules
    {
        "id": "CKV_AWS_158",
        "title": "CloudWatch Log Group Encryption",
        "description": "CloudWatch Log Group should have encryption enabled using KMS.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Logs::LogGroup"],
        "check": check_cloudwatch_log_encryption,
        "recommendation": "Enable encryption with a KMS key.",
        "terraform_fix": '''resource "aws_cloudwatch_log_group" "example" {
  name              = "/aws/example"
  kms_key_id        = aws_kms_key.logs.arn
  retention_in_days = 30
}''',
        "references": ["https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/encrypt-log-data-kms.html"],
    },
    # ECS Rules
    {
        "id": "CKV_AWS_65",
        "title": "ECS Container Insights",
        "description": "ECS cluster should have Container Insights enabled for monitoring.",
        "severity": "LOW",
        "resource_types": ["AWS::ECS::Cluster"],
        "check": check_ecs_container_insights,
        "recommendation": "Enable Container Insights in cluster settings.",
        "terraform_fix": '''resource "aws_ecs_cluster" "example" {
  name = "example"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-container-insights.html"],
    },
    # ECR Rules
    {
        "id": "CKV_AWS_33",
        "title": "ECR Scan on Push",
        "description": "ECR repository should have image scanning on push enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ECR::Repository"],
        "check": check_ecr_scan_on_push,
        "recommendation": "Enable image scanning on push.",
        "terraform_fix": '''resource "aws_ecr_repository" "example" {
  name = "example"

  image_scanning_configuration {
    scan_on_push = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html"],
    },
    {
        "id": "CKV_AWS_136",
        "title": "ECR Immutable Tags",
        "description": "ECR repository should use immutable image tags to prevent image overwrites.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ECR::Repository"],
        "check": check_ecr_immutable_tags,
        "recommendation": "Set image tag mutability to IMMUTABLE.",
        "terraform_fix": '''resource "aws_ecr_repository" "example" {
  name                 = "example"
  image_tag_mutability = "IMMUTABLE"
}''',
        "references": ["https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html"],
    },
    # EFS Rules
    {
        "id": "CKV_AWS_42",
        "title": "EFS Encryption at Rest",
        "description": "EFS file system should have encryption at rest enabled using KMS.",
        "severity": "HIGH",
        "resource_types": ["AWS::EFS::FileSystem"],
        "check": lambda props: not props.get("Encrypted", False),
        "recommendation": "Enable encryption at rest with a KMS key.",
        "terraform_fix": '''resource "aws_efs_file_system" "example" {
  encrypted  = true
  kms_key_id = aws_kms_key.efs.arn
}''',
        "references": ["https://docs.aws.amazon.com/efs/latest/ug/encryption-at-rest.html"],
    },
    # Neptune Rules
    {
        "id": "CKV_AWS_44",
        "title": "Neptune Cluster Encryption",
        "description": "Neptune DB cluster should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::Neptune::DBCluster"],
        "check": lambda props: not props.get("StorageEncrypted", False),
        "recommendation": "Enable storage encryption for the Neptune cluster.",
        "terraform_fix": '''resource "aws_neptune_cluster" "example" {
  storage_encrypted = true
  kms_key_arn       = aws_kms_key.neptune.arn
}''',
        "references": ["https://docs.aws.amazon.com/neptune/latest/userguide/encrypt.html"],
    },
    {
        "id": "CKV_AWS_101",
        "title": "Neptune Cluster Logging",
        "description": "Neptune DB cluster should have audit logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Neptune::DBCluster"],
        "check": lambda props: not props.get("EnableCloudwatchLogsExports", []),
        "recommendation": "Enable CloudWatch audit logs for Neptune cluster.",
        "terraform_fix": '''resource "aws_neptune_cluster" "example" {
  enable_cloudwatch_logs_exports = ["audit"]
}''',
        "references": ["https://docs.aws.amazon.com/neptune/latest/userguide/cloudwatch-logs.html"],
    },
    # DocumentDB Rules
    {
        "id": "CKV_AWS_74",
        "title": "DocumentDB Cluster Encryption",
        "description": "DocumentDB cluster should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::DocDB::DBCluster"],
        "check": lambda props: not props.get("StorageEncrypted", False),
        "recommendation": "Enable storage encryption for the DocumentDB cluster.",
        "terraform_fix": '''resource "aws_docdb_cluster" "example" {
  storage_encrypted = true
  kms_key_id        = aws_kms_key.docdb.arn
}''',
        "references": ["https://docs.aws.amazon.com/documentdb/latest/developerguide/encryption-at-rest.html"],
    },
    {
        "id": "CKV_AWS_75",
        "title": "DocumentDB Cluster Logging",
        "description": "DocumentDB cluster should have audit logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::DocDB::DBCluster"],
        "check": lambda props: "audit" not in props.get("EnableCloudwatchLogsExports", []),
        "recommendation": "Enable CloudWatch audit logs for DocumentDB cluster.",
        "terraform_fix": '''resource "aws_docdb_cluster" "example" {
  enabled_cloudwatch_logs_exports = ["audit", "profiler"]
}''',
        "references": ["https://docs.aws.amazon.com/documentdb/latest/developerguide/event-auditing.html"],
    },
    # Redshift Rules
    {
        "id": "CKV_AWS_64",
        "title": "Redshift Cluster Encryption",
        "description": "Redshift cluster should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::Redshift::Cluster"],
        "check": lambda props: not props.get("Encrypted", False),
        "recommendation": "Enable encryption for the Redshift cluster.",
        "terraform_fix": '''resource "aws_redshift_cluster" "example" {
  encrypted       = true
  kms_key_id      = aws_kms_key.redshift.arn
}''',
        "references": ["https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-db-encryption.html"],
    },
    {
        "id": "CKV_AWS_105",
        "title": "Redshift Public Accessibility",
        "description": "Redshift cluster should not be publicly accessible.",
        "severity": "CRITICAL",
        "resource_types": ["AWS::Redshift::Cluster"],
        "check": lambda props: props.get("PubliclyAccessible", False),
        "recommendation": "Disable public accessibility for Redshift cluster.",
        "terraform_fix": '''resource "aws_redshift_cluster" "example" {
  publicly_accessible = false
}''',
        "references": ["https://docs.aws.amazon.com/redshift/latest/mgmt/managing-clusters-vpc.html"],
    },
    {
        "id": "CKV_AWS_142",
        "title": "Redshift Logging",
        "description": "Redshift cluster should have audit logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Redshift::Cluster"],
        "check": lambda props: not props.get("LoggingProperties", {}),
        "recommendation": "Enable audit logging for Redshift cluster.",
        "terraform_fix": '''resource "aws_redshift_cluster" "example" {
  logging {
    enable        = true
    bucket_name   = aws_s3_bucket.logs.id
    s3_key_prefix = "redshift-logs/"
  }
}''',
        "references": ["https://docs.aws.amazon.com/redshift/latest/mgmt/db-auditing.html"],
    },
    # SageMaker Rules
    {
        "id": "CKV_AWS_122",
        "title": "SageMaker Notebook Encryption",
        "description": "SageMaker notebook instance should have encryption enabled with KMS.",
        "severity": "HIGH",
        "resource_types": ["AWS::SageMaker::NotebookInstance"],
        "check": lambda props: not props.get("KmsKeyId"),
        "recommendation": "Enable encryption with KMS for SageMaker notebook.",
        "terraform_fix": '''resource "aws_sagemaker_notebook_instance" "example" {
  kms_key_id = aws_kms_key.sagemaker.arn
}''',
        "references": ["https://docs.aws.amazon.com/sagemaker/latest/dg/encryption-at-rest.html"],
    },
    {
        "id": "CKV_AWS_123",
        "title": "SageMaker Notebook Direct Internet Access",
        "description": "SageMaker notebook should not have direct internet access.",
        "severity": "HIGH",
        "resource_types": ["AWS::SageMaker::NotebookInstance"],
        "check": lambda props: props.get("DirectInternetAccess", "Enabled") == "Enabled",
        "recommendation": "Disable direct internet access for SageMaker notebook.",
        "terraform_fix": '''resource "aws_sagemaker_notebook_instance" "example" {
  direct_internet_access = "Disabled"
  subnet_id              = aws_subnet.private.id
}''',
        "references": ["https://docs.aws.amazon.com/sagemaker/latest/dg/appendix-notebook-and-internet-access.html"],
    },
    {
        "id": "CKV_AWS_124",
        "title": "SageMaker Notebook Root Access",
        "description": "SageMaker notebook should have root access disabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::SageMaker::NotebookInstance"],
        "check": lambda props: props.get("RootAccess", "Enabled") == "Enabled",
        "recommendation": "Disable root access for SageMaker notebook.",
        "terraform_fix": '''resource "aws_sagemaker_notebook_instance" "example" {
  root_access = "Disabled"
}''',
        "references": ["https://docs.aws.amazon.com/sagemaker/latest/dg/nbi-root-access.html"],
    },
    # CloudTrail Rules
    {
        "id": "CKV_AWS_35",
        "title": "CloudTrail Encryption",
        "description": "CloudTrail should have encryption enabled using KMS.",
        "severity": "HIGH",
        "resource_types": ["AWS::CloudTrail::Trail"],
        "check": lambda props: not props.get("KMSKeyId"),
        "recommendation": "Enable KMS encryption for CloudTrail logs.",
        "terraform_fix": '''resource "aws_cloudtrail" "example" {
  kms_key_id = aws_kms_key.cloudtrail.arn
}''',
        "references": ["https://docs.aws.amazon.com/awscloudtrail/latest/userguide/encrypting-cloudtrail-log-files-with-aws-kms.html"],
    },
    {
        "id": "CKV_AWS_36",
        "title": "CloudTrail Log File Validation",
        "description": "CloudTrail should have log file validation enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::CloudTrail::Trail"],
        "check": lambda props: not props.get("EnableLogFileValidation", False),
        "recommendation": "Enable log file validation for CloudTrail.",
        "terraform_fix": '''resource "aws_cloudtrail" "example" {
  enable_log_file_validation = true
}''',
        "references": ["https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html"],
    },
    {
        "id": "CKV_AWS_67",
        "title": "CloudTrail Multi-Region",
        "description": "CloudTrail should be enabled for all regions.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::CloudTrail::Trail"],
        "check": lambda props: not props.get("IsMultiRegionTrail", False),
        "recommendation": "Enable multi-region for CloudTrail.",
        "terraform_fix": '''resource "aws_cloudtrail" "example" {
  is_multi_region_trail = true
}''',
        "references": ["https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html"],
    },
    # MemoryDB Rules
    {
        "id": "CKV_AWS_200",
        "title": "MemoryDB Encryption at Rest",
        "description": "MemoryDB cluster should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::MemoryDB::Cluster"],
        "check": lambda props: not props.get("KmsKeyId"),
        "recommendation": "Enable encryption at rest with KMS for MemoryDB.",
        "terraform_fix": '''resource "aws_memorydb_cluster" "example" {
  kms_key_arn = aws_kms_key.memorydb.arn
}''',
        "references": ["https://docs.aws.amazon.com/memorydb/latest/devguide/at-rest-encryption.html"],
    },
    {
        "id": "CKV_AWS_201",
        "title": "MemoryDB TLS Encryption",
        "description": "MemoryDB cluster should have TLS enabled for in-transit encryption.",
        "severity": "HIGH",
        "resource_types": ["AWS::MemoryDB::Cluster"],
        "check": lambda props: not props.get("TLSEnabled", True),
        "recommendation": "Enable TLS for MemoryDB cluster.",
        "terraform_fix": '''resource "aws_memorydb_cluster" "example" {
  tls_enabled = true
}''',
        "references": ["https://docs.aws.amazon.com/memorydb/latest/devguide/in-transit-encryption.html"],
    },
    # Kinesis Rules
    {
        "id": "CKV_AWS_43",
        "title": "Kinesis Stream Encryption",
        "description": "Kinesis stream should have encryption enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::Kinesis::Stream"],
        "check": lambda props: props.get("StreamEncryption", {}).get("EncryptionType") != "KMS",
        "recommendation": "Enable KMS encryption for Kinesis stream.",
        "terraform_fix": '''resource "aws_kinesis_stream" "example" {
  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.kinesis.id
}''',
        "references": ["https://docs.aws.amazon.com/streams/latest/dev/server-side-encryption.html"],
    },
    # MSK Rules
    {
        "id": "CKV_AWS_80",
        "title": "MSK Encryption at Rest",
        "description": "MSK cluster should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::MSK::Cluster"],
        "check": lambda props: not props.get("EncryptionInfo", {}).get("EncryptionAtRest", {}).get("DataVolumeKMSKeyId"),
        "recommendation": "Enable encryption at rest with KMS for MSK cluster.",
        "terraform_fix": '''resource "aws_msk_cluster" "example" {
  encryption_info {
    encryption_at_rest_kms_key_arn = aws_kms_key.msk.arn
  }
}''',
        "references": ["https://docs.aws.amazon.com/msk/latest/developerguide/msk-encryption.html"],
    },
    {
        "id": "CKV_AWS_81",
        "title": "MSK In-Transit Encryption",
        "description": "MSK cluster should have in-transit encryption enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::MSK::Cluster"],
        "check": lambda props: props.get("EncryptionInfo", {}).get("EncryptionInTransit", {}).get("ClientBroker") != "TLS",
        "recommendation": "Enable TLS encryption for client-broker communication.",
        "terraform_fix": '''resource "aws_msk_cluster" "example" {
  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/msk/latest/developerguide/msk-encryption.html"],
    },
    # OpenSearch Rules
    {
        "id": "CKV_AWS_84",
        "title": "OpenSearch Encryption at Rest",
        "description": "OpenSearch domain should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::OpenSearchService::Domain", "AWS::Elasticsearch::Domain"],
        "check": lambda props: not props.get("EncryptionAtRestOptions", {}).get("Enabled", False),
        "recommendation": "Enable encryption at rest for OpenSearch domain.",
        "terraform_fix": '''resource "aws_opensearch_domain" "example" {
  encrypt_at_rest {
    enabled    = true
    kms_key_id = aws_kms_key.opensearch.id
  }
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/encryption-at-rest.html"],
    },
    {
        "id": "CKV_AWS_85",
        "title": "OpenSearch Node-to-Node Encryption",
        "description": "OpenSearch domain should have node-to-node encryption enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::OpenSearchService::Domain", "AWS::Elasticsearch::Domain"],
        "check": lambda props: not props.get("NodeToNodeEncryptionOptions", {}).get("Enabled", False),
        "recommendation": "Enable node-to-node encryption for OpenSearch domain.",
        "terraform_fix": '''resource "aws_opensearch_domain" "example" {
  node_to_node_encryption {
    enabled = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/ntn.html"],
    },
    {
        "id": "CKV_AWS_137",
        "title": "OpenSearch HTTPS Required",
        "description": "OpenSearch domain should enforce HTTPS.",
        "severity": "HIGH",
        "resource_types": ["AWS::OpenSearchService::Domain", "AWS::Elasticsearch::Domain"],
        "check": lambda props: not props.get("DomainEndpointOptions", {}).get("EnforceHTTPS", False),
        "recommendation": "Enforce HTTPS for OpenSearch domain endpoint.",
        "terraform_fix": '''resource "aws_opensearch_domain" "example" {
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/security.html"],
    },
    # Network Firewall Rules
    {
        "id": "CKV_AWS_143",
        "title": "Network Firewall Encryption",
        "description": "Network Firewall should have encryption configuration.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::NetworkFirewall::Firewall"],
        "check": lambda props: not props.get("EncryptionConfiguration", {}).get("KeyId"),
        "recommendation": "Enable KMS encryption for Network Firewall.",
        "terraform_fix": '''resource "aws_networkfirewall_firewall" "example" {
  encryption_configuration {
    type   = "CUSTOMER_KMS"
    key_id = aws_kms_key.firewall.arn
  }
}''',
        "references": ["https://docs.aws.amazon.com/network-firewall/latest/developerguide/encryption-at-rest.html"],
    },
    # Glue Rules
    {
        "id": "CKV_AWS_94",
        "title": "Glue Job Encryption",
        "description": "Glue job should have security configuration with encryption.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Glue::Job"],
        "check": lambda props: not props.get("SecurityConfiguration"),
        "recommendation": "Attach a security configuration with encryption to the Glue job.",
        "terraform_fix": '''resource "aws_glue_job" "example" {
  security_configuration = aws_glue_security_configuration.example.name
}''',
        "references": ["https://docs.aws.amazon.com/glue/latest/dg/encryption-security-configuration.html"],
    },
    # Athena Rules
    {
        "id": "CKV_AWS_82",
        "title": "Athena Workgroup Encryption",
        "description": "Athena workgroup should have encryption enabled for query results.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Athena::WorkGroup"],
        "check": lambda props: not props.get("WorkGroupConfiguration", {}).get("ResultConfiguration", {}).get("EncryptionConfiguration"),
        "recommendation": "Enable encryption for Athena query results.",
        "terraform_fix": '''resource "aws_athena_workgroup" "example" {
  configuration {
    result_configuration {
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = aws_kms_key.athena.arn
      }
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/athena/latest/ug/encryption.html"],
    },
    # Step Functions Rules
    {
        "id": "CKV_AWS_138",
        "title": "Step Functions Logging",
        "description": "Step Functions state machine should have logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::StepFunctions::StateMachine"],
        "check": lambda props: not props.get("LoggingConfiguration", {}).get("Destinations"),
        "recommendation": "Enable CloudWatch logging for Step Functions.",
        "terraform_fix": '''resource "aws_sfn_state_machine" "example" {
  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }
}''',
        "references": ["https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html"],
    },
    # API Gateway Rules
    {
        "id": "CKV_AWS_95",
        "title": "API Gateway Access Logging",
        "description": "API Gateway stage should have access logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ApiGateway::Stage"],
        "check": lambda props: not props.get("AccessLogSetting", {}).get("DestinationArn"),
        "recommendation": "Enable access logging for API Gateway stage.",
        "terraform_fix": '''resource "aws_api_gateway_stage" "example" {
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api.arn
    format          = "$requestId"
  }
}''',
        "references": ["https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-logging.html"],
    },
    {
        "id": "CKV_AWS_76",
        "title": "API Gateway X-Ray Tracing",
        "description": "API Gateway stage should have X-Ray tracing enabled.",
        "severity": "LOW",
        "resource_types": ["AWS::ApiGateway::Stage"],
        "check": lambda props: not props.get("TracingEnabled", False),
        "recommendation": "Enable X-Ray tracing for API Gateway stage.",
        "terraform_fix": '''resource "aws_api_gateway_stage" "example" {
  xray_tracing_enabled = true
}''',
        "references": ["https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-xray.html"],
    },
    # Transfer Family Rules
    {
        "id": "CKV_AWS_164",
        "title": "Transfer Server Public Endpoint",
        "description": "AWS Transfer server should not use public endpoint type.",
        "severity": "HIGH",
        "resource_types": ["AWS::Transfer::Server"],
        "check": lambda props: props.get("EndpointType") == "PUBLIC",
        "recommendation": "Use VPC endpoint instead of public endpoint.",
        "terraform_fix": '''resource "aws_transfer_server" "example" {
  endpoint_type = "VPC"
  endpoint_details {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.transfer.id]
  }
}''',
        "references": ["https://docs.aws.amazon.com/transfer/latest/userguide/create-server-in-vpc.html"],
    },
    # WAFv2 Rules
    {
        "id": "CKV_AWS_192",
        "title": "WAFv2 WebACL Logging",
        "description": "WAFv2 WebACL should have logging enabled for security monitoring.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::WAFv2::WebACL"],
        "check": lambda props: True,  # Logging is a separate resource, recommend enabling
        "recommendation": "Enable logging for WAFv2 WebACL using aws_wafv2_web_acl_logging_configuration.",
        "terraform_fix": '''resource "aws_wafv2_web_acl_logging_configuration" "example" {
  log_destination_configs = [aws_kinesis_firehose_delivery_stream.example.arn]
  resource_arn            = aws_wafv2_web_acl.example.arn

  logging_filter {
    default_behavior = "KEEP"
    filter {
      behavior    = "DROP"
      requirement = "MEETS_ANY"
      condition {
        action_condition {
          action = "ALLOW"
        }
      }
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/logging.html"],
    },
    {
        "id": "CKV_AWS_193",
        "title": "WAFv2 WebACL CloudWatch Metrics",
        "description": "WAFv2 WebACL should have CloudWatch metrics enabled.",
        "severity": "LOW",
        "resource_types": ["AWS::WAFv2::WebACL"],
        "check": lambda props: not props.get("VisibilityConfig", {}).get("CloudWatchMetricsEnabled", False),
        "recommendation": "Enable CloudWatch metrics for WAFv2 WebACL.",
        "terraform_fix": '''resource "aws_wafv2_web_acl" "example" {
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "example-waf-metrics"
    sampled_requests_enabled   = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/monitoring-cloudwatch.html"],
    },
    {
        "id": "CKV_AWS_194",
        "title": "WAFv2 WebACL Sampled Requests",
        "description": "WAFv2 WebACL should have sampled requests enabled for debugging.",
        "severity": "LOW",
        "resource_types": ["AWS::WAFv2::WebACL"],
        "check": lambda props: not props.get("VisibilityConfig", {}).get("SampledRequestsEnabled", False),
        "recommendation": "Enable sampled requests for WAFv2 WebACL.",
        "terraform_fix": '''resource "aws_wafv2_web_acl" "example" {
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "example-waf-metrics"
    sampled_requests_enabled   = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/web-acl-testing.html"],
    },
    {
        "id": "CKV_AWS_195",
        "title": "WAFv2 Rule Group Metrics",
        "description": "WAFv2 Rule Group should have CloudWatch metrics enabled.",
        "severity": "LOW",
        "resource_types": ["AWS::WAFv2::RuleGroup"],
        "check": lambda props: not props.get("VisibilityConfig", {}).get("CloudWatchMetricsEnabled", False),
        "recommendation": "Enable CloudWatch metrics for WAFv2 Rule Group.",
        "terraform_fix": '''resource "aws_wafv2_rule_group" "example" {
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "example-rule-group"
    sampled_requests_enabled   = true
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-groups.html"],
    },
    # WAF Classic Rules
    {
        "id": "CKV_AWS_196",
        "title": "WAF Classic WebACL Has Rules",
        "description": "WAF Classic WebACL should have at least one rule configured.",
        "severity": "HIGH",
        "resource_types": ["AWS::WAF::WebACL", "AWS::WAFRegional::WebACL"],
        "check": lambda props: not props.get("Rules", []),
        "recommendation": "Add rules to the WAF Classic WebACL. Consider migrating to WAFv2.",
        "terraform_fix": '''# Consider migrating to WAFv2 for better features
resource "aws_wafregional_web_acl" "example" {
  name        = "example"
  metric_name = "example"

  default_action {
    type = "BLOCK"
  }

  rule {
    action {
      type = "BLOCK"
    }
    priority = 1
    rule_id  = aws_wafregional_rule.example.id
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/classic-web-acl.html"],
    },
    {
        "id": "CKV_AWS_197",
        "title": "WAF Classic Default Action Block",
        "description": "WAF Classic WebACL should have default action set to BLOCK for better security.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::WAF::WebACL", "AWS::WAFRegional::WebACL"],
        "check": lambda props: props.get("DefaultAction", {}).get("Type") != "BLOCK",
        "recommendation": "Set default action to BLOCK and explicitly allow known good traffic.",
        "terraform_fix": '''resource "aws_wafregional_web_acl" "example" {
  default_action {
    type = "BLOCK"
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/classic-web-acl-default-action.html"],
    },
    # AWS Shield Rules
    {
        "id": "CKV_AWS_198",
        "title": "Shield Protection for Critical Resources",
        "description": "Critical resources should have AWS Shield Advanced protection enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::Shield::Protection"],
        "check": lambda props: False,  # Having Shield protection is good
        "recommendation": "Ensure Shield Advanced protection is enabled for all critical resources (ALB, CloudFront, Route53, etc.).",
        "terraform_fix": '''resource "aws_shield_protection" "example" {
  name         = "example-protection"
  resource_arn = aws_lb.example.arn

  tags = {
    Environment = "production"
  }
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html"],
    },
    {
        "id": "CKV_AWS_199",
        "title": "Shield Protection Group Coverage",
        "description": "Shield Protection Group should be configured for aggregated DDoS protection.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Shield::ProtectionGroup"],
        "check": lambda props: False,  # Having a protection group is good
        "recommendation": "Create Shield Protection Groups to aggregate protection for related resources.",
        "terraform_fix": '''resource "aws_shield_protection_group" "example" {
  protection_group_id = "example-group"
  aggregation         = "MAX"
  pattern             = "BY_RESOURCE_TYPE"
  resource_type       = "APPLICATION_LOAD_BALANCER"
}''',
        "references": ["https://docs.aws.amazon.com/waf/latest/developerguide/ddos-manage-protection-groups.html"],
    },
    # Firewall Manager Rules
    {
        "id": "CKV_AWS_300",
        "title": "FMS Policy Auto Remediation",
        "description": "Firewall Manager policy should have auto-remediation enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::FMS::Policy"],
        "check": lambda props: not props.get("RemediationEnabled", False),
        "recommendation": "Enable auto-remediation for Firewall Manager policy.",
        "terraform_fix": '''resource "aws_fms_policy" "example" {
  name                  = "example"
  remediation_enabled   = true
  resource_type         = "AWS::ElasticLoadBalancingV2::LoadBalancer"
  exclude_resource_tags = false

  security_service_policy_data {
    type = "WAF"
  }
}''',
        "references": ["https://docs.aws.amazon.com/fms/latest/userguide/fms-policy-scope.html"],
    },
    # ElastiCache Rules
    {
        "id": "CKV_AWS_301",
        "title": "ElastiCache Encryption at Rest",
        "description": "ElastiCache replication group should have encryption at rest enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::ElastiCache::ReplicationGroup"],
        "check": lambda props: not props.get("AtRestEncryptionEnabled", False),
        "recommendation": "Enable encryption at rest for ElastiCache replication group.",
        "terraform_fix": '''resource "aws_elasticache_replication_group" "example" {
  at_rest_encryption_enabled = true
  kms_key_id                 = aws_kms_key.elasticache.arn
}''',
        "references": ["https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/at-rest-encryption.html"],
    },
    {
        "id": "CKV_AWS_302",
        "title": "ElastiCache In-Transit Encryption",
        "description": "ElastiCache replication group should have encryption in transit enabled.",
        "severity": "HIGH",
        "resource_types": ["AWS::ElastiCache::ReplicationGroup"],
        "check": lambda props: not props.get("TransitEncryptionEnabled", False),
        "recommendation": "Enable encryption in transit for ElastiCache replication group.",
        "terraform_fix": '''resource "aws_elasticache_replication_group" "example" {
  transit_encryption_enabled = true
}''',
        "references": ["https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/in-transit-encryption.html"],
    },
    {
        "id": "CKV_AWS_303",
        "title": "ElastiCache Auth Token",
        "description": "ElastiCache replication group should have AUTH token enabled for Redis.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ElastiCache::ReplicationGroup"],
        "check": lambda props: not props.get("AuthToken"),
        "recommendation": "Enable AUTH token for Redis ElastiCache cluster.",
        "terraform_fix": '''resource "aws_elasticache_replication_group" "example" {
  auth_token                 = var.redis_auth_token
  transit_encryption_enabled = true  # Required for auth_token
}''',
        "references": ["https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/auth.html"],
    },
    # CloudFront Rules
    {
        "id": "CKV_AWS_304",
        "title": "CloudFront WAF Integration",
        "description": "CloudFront distribution should have WAF WebACL associated.",
        "severity": "HIGH",
        "resource_types": ["AWS::CloudFront::Distribution"],
        "check": lambda props: not props.get("DistributionConfig", {}).get("WebACLId"),
        "recommendation": "Associate a WAFv2 WebACL with the CloudFront distribution.",
        "terraform_fix": '''resource "aws_cloudfront_distribution" "example" {
  web_acl_id = aws_wafv2_web_acl.example.arn
}''',
        "references": ["https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html"],
    },
    {
        "id": "CKV_AWS_305",
        "title": "CloudFront HTTPS Only",
        "description": "CloudFront distribution should require HTTPS for viewer connections.",
        "severity": "HIGH",
        "resource_types": ["AWS::CloudFront::Distribution"],
        "check": lambda props: props.get("DistributionConfig", {}).get("DefaultCacheBehavior", {}).get("ViewerProtocolPolicy") != "https-only",
        "recommendation": "Set viewer protocol policy to https-only or redirect-to-https.",
        "terraform_fix": '''resource "aws_cloudfront_distribution" "example" {
  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-https.html"],
    },
    {
        "id": "CKV_AWS_306",
        "title": "CloudFront Minimum TLS Version",
        "description": "CloudFront distribution should use TLS 1.2 or higher.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::CloudFront::Distribution"],
        "check": lambda props: props.get("DistributionConfig", {}).get("ViewerCertificate", {}).get("MinimumProtocolVersion", "TLSv1") in ["SSLv3", "TLSv1", "TLSv1_2016"],
        "recommendation": "Set minimum protocol version to TLSv1.2_2021 or higher.",
        "terraform_fix": '''resource "aws_cloudfront_distribution" "example" {
  viewer_certificate {
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }
}''',
        "references": ["https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/secure-connections-supported-viewer-protocols-ciphers.html"],
    },
    # ALB/NLB Rules
    {
        "id": "CKV_AWS_307",
        "title": "ALB WAF Integration",
        "description": "Application Load Balancer should have WAF WebACL associated.",
        "severity": "HIGH",
        "resource_types": ["AWS::ElasticLoadBalancingV2::LoadBalancer"],
        "check": lambda props: props.get("Type") == "application",  # ALBs should have WAF
        "recommendation": "Associate a WAFv2 WebACL with the Application Load Balancer.",
        "terraform_fix": '''resource "aws_wafv2_web_acl_association" "example" {
  resource_arn = aws_lb.example.arn
  web_acl_arn  = aws_wafv2_web_acl.example.arn
}''',
        "references": ["https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html#load-balancer-waf"],
    },
    {
        "id": "CKV_AWS_308",
        "title": "ALB Deletion Protection",
        "description": "Application Load Balancer should have deletion protection enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::ElasticLoadBalancingV2::LoadBalancer"],
        "check": lambda props: not any(
            attr.get("Key") == "deletion_protection.enabled" and attr.get("Value") == "true"
            for attr in props.get("LoadBalancerAttributes", [])
        ),
        "recommendation": "Enable deletion protection for production load balancers.",
        "terraform_fix": '''resource "aws_lb" "example" {
  enable_deletion_protection = true
}''',
        "references": ["https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html#deletion-protection"],
    },
    # OpenSearch Serverless Rules
    {
        "id": "CKV_AWS_309",
        "title": "OpenSearch Serverless Encryption Policy",
        "description": "OpenSearch Serverless collection should have encryption security policy.",
        "severity": "HIGH",
        "resource_types": ["AWS::OpenSearchServerless::Collection"],
        "check": lambda props: True,  # Encryption policy should be created separately
        "recommendation": "Create an encryption security policy for the OpenSearch Serverless collection.",
        "terraform_fix": '''resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "example-encryption"
  type = "encryption"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/example"]
    }]
    AWSOwnedKey = true
  })
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-encryption.html"],
    },
    {
        "id": "CKV_AWS_310",
        "title": "OpenSearch Serverless Network Policy",
        "description": "OpenSearch Serverless collection should have a network security policy.",
        "severity": "HIGH",
        "resource_types": ["AWS::OpenSearchServerless::Collection"],
        "check": lambda props: True,  # Network policy should be created separately
        "recommendation": "Create a network security policy to control access to OpenSearch Serverless.",
        "terraform_fix": '''resource "aws_opensearchserverless_security_policy" "network" {
  name = "example-network"
  type = "network"
  policy = jsonencode([{
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/example"]
    }]
    AllowFromPublic = false
    SourceVPCEs     = [aws_opensearchserverless_vpc_endpoint.example.id]
  }])
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-network.html"],
    },
    {
        "id": "CKV_AWS_311",
        "title": "OpenSearch Serverless Access Policy",
        "description": "OpenSearch Serverless collection should have a data access policy.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::OpenSearchServerless::Collection"],
        "check": lambda props: True,  # Access policy should be created separately
        "recommendation": "Create a data access policy to control access to OpenSearch Serverless data.",
        "terraform_fix": '''resource "aws_opensearchserverless_access_policy" "example" {
  name = "example-access"
  type = "data"
  policy = jsonencode([{
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/example"]
      Permission   = ["aoss:*"]
    }]
    Principal = [data.aws_caller_identity.current.arn]
  }])
}''',
        "references": ["https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-data-access.html"],
    },
    # Bedrock Rules
    {
        "id": "CKV_AWS_312",
        "title": "Bedrock Guardrail Configuration",
        "description": "Bedrock agent should have guardrails configured to prevent harmful outputs.",
        "severity": "HIGH",
        "resource_types": ["AWS::Bedrock::Agent"],
        "check": lambda props: not props.get("GuardrailConfiguration"),
        "recommendation": "Configure guardrails for Bedrock agent to ensure responsible AI usage.",
        "terraform_fix": '''resource "aws_bedrockagent_agent" "example" {
  agent_name = "example"

  guardrail_configuration {
    guardrail_identifier = aws_bedrock_guardrail.example.guardrail_id
    guardrail_version    = "DRAFT"
  }
}''',
        "references": ["https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html"],
    },
    {
        "id": "CKV_AWS_313",
        "title": "Bedrock Knowledge Base Encryption",
        "description": "Bedrock knowledge base should use customer managed KMS key for encryption.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::Bedrock::KnowledgeBase"],
        "check": lambda props: not props.get("KnowledgeBaseConfiguration", {}).get("VectorKnowledgeBaseConfiguration", {}).get("EmbeddingModelConfiguration"),
        "recommendation": "Configure proper embedding model and encryption for Bedrock knowledge base.",
        "terraform_fix": '''resource "aws_bedrockagent_knowledge_base" "example" {
  name = "example"

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html"],
    },
    {
        "id": "CKV_AWS_314",
        "title": "Bedrock Guardrail Content Filtering",
        "description": "Bedrock guardrail should have content filters configured.",
        "severity": "HIGH",
        "resource_types": ["AWS::Bedrock::Guardrail"],
        "check": lambda props: not props.get("ContentPolicyConfig"),
        "recommendation": "Configure content policy filters in Bedrock guardrail.",
        "terraform_fix": '''resource "aws_bedrock_guardrail" "example" {
  name = "example"

  content_policy_config {
    filters_config {
      type            = "HATE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
    filters_config {
      type            = "VIOLENCE"
      input_strength  = "HIGH"
      output_strength = "HIGH"
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-content-filters.html"],
    },
    # Security Lake Rules
    {
        "id": "CKV_AWS_315",
        "title": "Security Lake Encryption",
        "description": "Security Lake data lake should use customer managed KMS key.",
        "severity": "HIGH",
        "resource_types": ["AWS::SecurityLake::DataLake"],
        "check": lambda props: not any(
            config.get("EncryptionConfiguration", {}).get("KmsKeyId")
            for config in props.get("Configurations", [])
        ),
        "recommendation": "Configure customer managed KMS encryption for Security Lake.",
        "terraform_fix": '''resource "aws_securitylake_data_lake" "example" {
  meta_store_manager_role_arn = aws_iam_role.security_lake.arn

  configuration {
    encryption_configuration {
      kms_key_id = aws_kms_key.security_lake.id
    }
    region = "us-east-1"
  }
}''',
        "references": ["https://docs.aws.amazon.com/security-lake/latest/userguide/encryption.html"],
    },
    # VPC Lattice Rules
    {
        "id": "CKV_AWS_316",
        "title": "VPC Lattice Service Auth Policy",
        "description": "VPC Lattice service should have an auth policy configured.",
        "severity": "HIGH",
        "resource_types": ["AWS::VpcLattice::Service"],
        "check": lambda props: props.get("AuthType") != "AWS_IAM",
        "recommendation": "Configure AWS IAM authentication for VPC Lattice service.",
        "terraform_fix": '''resource "aws_vpclattice_service" "example" {
  name      = "example"
  auth_type = "AWS_IAM"
}

resource "aws_vpclattice_auth_policy" "example" {
  resource_identifier = aws_vpclattice_service.example.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "vpc-lattice-svcs:Invoke"
      Resource  = "*"
      Condition = {
        StringEquals = {
          "vpc-lattice-svcs:ServiceNetworkArn" = aws_vpclattice_service_network.example.arn
        }
      }
    }]
  })
}''',
        "references": ["https://docs.aws.amazon.com/vpc-lattice/latest/ug/auth-policies.html"],
    },
    {
        "id": "CKV_AWS_317",
        "title": "VPC Lattice Access Logging",
        "description": "VPC Lattice service network should have access logging enabled.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::VpcLattice::ServiceNetwork"],
        "check": lambda props: True,  # Access logging is a separate resource
        "recommendation": "Enable access logging for VPC Lattice service network.",
        "terraform_fix": '''resource "aws_vpclattice_access_log_subscription" "example" {
  resource_identifier = aws_vpclattice_service_network.example.arn
  destination_arn     = aws_cloudwatch_log_group.lattice.arn
}''',
        "references": ["https://docs.aws.amazon.com/vpc-lattice/latest/ug/monitoring-access-logs.html"],
    },
    # Verified Access Rules
    {
        "id": "CKV_AWS_318",
        "title": "Verified Access Trust Provider",
        "description": "Verified Access instance should have a trust provider configured.",
        "severity": "HIGH",
        "resource_types": ["AWS::EC2::VerifiedAccessInstance"],
        "check": lambda props: not props.get("VerifiedAccessTrustProviders"),
        "recommendation": "Configure a trust provider for Verified Access.",
        "terraform_fix": '''resource "aws_verifiedaccess_trust_provider" "example" {
  policy_reference_name    = "example"
  trust_provider_type      = "user"
  user_trust_provider_type = "iam-identity-center"
}

resource "aws_verifiedaccess_instance_trust_provider_attachment" "example" {
  verifiedaccess_instance_id       = aws_verifiedaccess_instance.example.id
  verifiedaccess_trust_provider_id = aws_verifiedaccess_trust_provider.example.id
}''',
        "references": ["https://docs.aws.amazon.com/verified-access/latest/ug/trust-providers.html"],
    },
    # Managed Prometheus Rules
    {
        "id": "CKV_AWS_319",
        "title": "Prometheus Workspace Logging",
        "description": "Managed Prometheus workspace should have logging configured.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::APS::Workspace"],
        "check": lambda props: not props.get("LoggingConfiguration", {}).get("LogGroupArn"),
        "recommendation": "Configure logging for Managed Prometheus workspace.",
        "terraform_fix": '''resource "aws_prometheus_workspace" "example" {
  alias = "example"

  logging_configuration {
    log_group_arn = "${aws_cloudwatch_log_group.prometheus.arn}:*"
  }
}''',
        "references": ["https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-onboard-logging.html"],
    },
    # Kinesis Analytics Rules
    {
        "id": "CKV_AWS_320",
        "title": "Kinesis Analytics Application VPC",
        "description": "Kinesis Analytics application should be deployed in a VPC for network isolation.",
        "severity": "MEDIUM",
        "resource_types": ["AWS::KinesisAnalyticsV2::Application"],
        "check": lambda props: not props.get("ApplicationConfiguration", {}).get("VpcConfigurations"),
        "recommendation": "Deploy Kinesis Analytics application within a VPC.",
        "terraform_fix": '''resource "aws_kinesisanalyticsv2_application" "example" {
  name                   = "example"
  runtime_environment    = "FLINK-1_15"
  service_execution_role = aws_iam_role.kinesis.arn

  application_configuration {
    vpc_configuration {
      security_group_ids = [aws_security_group.kinesis.id]
      subnet_ids         = [aws_subnet.private.id]
    }
  }
}''',
        "references": ["https://docs.aws.amazon.com/kinesisanalytics/latest/java/vpc.html"],
    },
]


def get_rules_for_resource_type(resource_type: str) -> List[Dict[str, Any]]:
    """Get all security rules applicable to a resource type."""
    return [
        rule for rule in SECURITY_RULES
        if resource_type in rule.get("resource_types", [])
    ]


def get_rules_by_severity(severity: str) -> List[Dict[str, Any]]:
    """Get all security rules of a specific severity."""
    return [
        rule for rule in SECURITY_RULES
        if rule.get("severity") == severity
    ]
