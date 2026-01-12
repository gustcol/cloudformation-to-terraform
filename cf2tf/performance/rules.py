"""
Performance Rules and Best Practices

This module contains performance recommendations that are checked against
CloudFormation resources during conversion.
"""

from typing import Any, Callable, Dict, List, Optional


def check_ec2_instance_type(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check for outdated or suboptimal EC2 instance types."""
    instance_type = properties.get("InstanceType", "")

    # Outdated instance families
    outdated_families = ["t1", "m1", "m2", "m3", "c1", "c3", "r3", "i2", "hs1", "g2"]
    family = instance_type.split(".")[0] if instance_type else ""

    if family in outdated_families:
        return {
            "issue": "outdated_instance_family",
            "current": instance_type,
            "suggestion": f"Consider upgrading from {family}.* to a newer generation",
        }

    # Check for burstable instances in production scenarios
    if family in ["t2", "t3", "t3a"]:
        return {
            "issue": "burstable_instance",
            "current": instance_type,
            "suggestion": "Burstable instances may not be suitable for consistent workloads",
        }

    return None


def check_ec2_ebs_optimization(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check if EBS optimization is enabled."""
    if not properties.get("EbsOptimized", False):
        return {
            "issue": "ebs_not_optimized",
            "suggestion": "Enable EBS optimization for better I/O performance",
        }
    return None


def check_ec2_detailed_monitoring(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check if detailed monitoring is enabled."""
    monitoring = properties.get("Monitoring", False)
    if not monitoring:
        return {
            "issue": "basic_monitoring",
            "suggestion": "Enable detailed monitoring for 1-minute metrics",
        }
    return None


def check_rds_instance_class(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check for outdated or suboptimal RDS instance classes."""
    instance_class = properties.get("DBInstanceClass", "")

    # Outdated instance classes
    if instance_class.startswith("db.m3") or instance_class.startswith("db.r3"):
        return {
            "issue": "outdated_instance_class",
            "current": instance_class,
            "suggestion": "Consider upgrading to db.m5/m6 or db.r5/r6 for better performance",
        }

    # Small instances for production
    small_classes = ["db.t2.micro", "db.t2.small", "db.t3.micro", "db.t3.small"]
    if instance_class in small_classes:
        return {
            "issue": "small_instance",
            "current": instance_class,
            "suggestion": "Consider larger instance class for production workloads",
        }

    return None


def check_rds_storage_type(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check RDS storage type configuration."""
    storage_type = properties.get("StorageType", "standard")

    if storage_type == "standard":
        return {
            "issue": "magnetic_storage",
            "suggestion": "Use gp3 or io1 storage for better performance",
        }

    if storage_type == "gp2":
        return {
            "issue": "gp2_storage",
            "suggestion": "Consider migrating to gp3 for cost savings and better baseline performance",
        }

    return None


def check_rds_performance_insights(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check if Performance Insights is enabled."""
    if not properties.get("EnablePerformanceInsights", False):
        return {
            "issue": "no_performance_insights",
            "suggestion": "Enable Performance Insights for database monitoring",
        }
    return None


def check_dynamodb_capacity_mode(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check DynamoDB capacity mode configuration."""
    billing_mode = properties.get("BillingMode", "PROVISIONED")
    throughput = properties.get("ProvisionedThroughput", {})

    if billing_mode == "PROVISIONED":
        read_capacity = throughput.get("ReadCapacityUnits", 0)
        write_capacity = throughput.get("WriteCapacityUnits", 0)

        if read_capacity < 5 or write_capacity < 5:
            return {
                "issue": "low_provisioned_capacity",
                "suggestion": "Consider using On-Demand capacity mode for variable workloads",
            }

    return None


def check_dynamodb_auto_scaling(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check if DynamoDB uses auto scaling."""
    billing_mode = properties.get("BillingMode", "PROVISIONED")

    if billing_mode == "PROVISIONED":
        return {
            "issue": "no_auto_scaling_mentioned",
            "suggestion": "Configure Application Auto Scaling for DynamoDB tables",
        }

    return None


def check_lambda_memory(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check Lambda function memory configuration."""
    memory = properties.get("MemorySize", 128)

    if memory == 128:
        return {
            "issue": "minimum_memory",
            "current": memory,
            "suggestion": "Consider increasing memory for better CPU allocation and performance",
        }

    return None


def check_lambda_timeout(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check Lambda function timeout configuration."""
    timeout = properties.get("Timeout", 3)

    if timeout == 3:
        return {
            "issue": "default_timeout",
            "current": timeout,
            "suggestion": "Configure appropriate timeout based on function execution time",
        }

    if timeout > 60:
        return {
            "issue": "long_timeout",
            "current": timeout,
            "suggestion": "Consider using Step Functions for long-running processes",
        }

    return None


def check_lambda_provisioned_concurrency(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check for Lambda cold start optimization."""
    reserved = properties.get("ReservedConcurrentExecutions")

    if reserved is None:
        return {
            "issue": "no_provisioned_concurrency",
            "suggestion": "Consider Provisioned Concurrency for latency-sensitive functions",
        }

    return None


def check_s3_storage_class(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check S3 lifecycle policies for cost optimization."""
    lifecycle = properties.get("LifecycleConfiguration", {})
    rules = lifecycle.get("Rules", [])

    if not rules:
        return {
            "issue": "no_lifecycle_rules",
            "suggestion": "Configure lifecycle rules to transition data to cheaper storage classes",
        }

    return None


def check_s3_transfer_acceleration(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check S3 transfer acceleration configuration."""
    acceleration = properties.get("AccelerateConfiguration", {})

    if not acceleration.get("AccelerationStatus") == "Enabled":
        return {
            "issue": "no_transfer_acceleration",
            "suggestion": "Enable Transfer Acceleration for faster uploads from distant locations",
        }

    return None


def check_alb_idle_timeout(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check ALB idle timeout configuration."""
    attributes = properties.get("LoadBalancerAttributes", [])

    for attr in attributes:
        if attr.get("Key") == "idle_timeout.timeout_seconds":
            timeout = int(attr.get("Value", 60))
            if timeout > 60:
                return {
                    "issue": "high_idle_timeout",
                    "current": timeout,
                    "suggestion": "Consider lower idle timeout to release connections faster",
                }

    return None


def check_elasticache_node_type(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check ElastiCache node type."""
    node_type = properties.get("CacheNodeType", "")

    if node_type.startswith("cache.t2") or node_type.startswith("cache.m3"):
        return {
            "issue": "outdated_node_type",
            "current": node_type,
            "suggestion": "Consider upgrading to cache.r6g or cache.m6g for better performance",
        }

    return None


def check_cloudfront_caching(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check CloudFront caching configuration."""
    default_cache = properties.get("DefaultCacheBehavior", {})
    min_ttl = default_cache.get("MinTTL", 0)
    default_ttl = default_cache.get("DefaultTTL", 86400)

    if min_ttl == 0 and default_ttl <= 86400:
        return {
            "issue": "suboptimal_caching",
            "suggestion": "Configure appropriate cache TTLs based on content type",
        }

    return None


def check_api_gateway_caching(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check API Gateway caching configuration."""
    if not properties.get("CacheClusterEnabled", False):
        return {
            "issue": "no_api_caching",
            "suggestion": "Enable API Gateway caching for frequently accessed endpoints",
        }

    return None


def check_ecs_resource_allocation(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check ECS task resource allocation."""
    cpu = properties.get("Cpu")
    memory = properties.get("Memory")

    if cpu and memory:
        cpu_val = int(cpu)
        memory_val = int(memory)

        # Check for common misconfigurations
        if cpu_val == 256 and memory_val > 1024:
            return {
                "issue": "cpu_memory_imbalance",
                "suggestion": "Consider increasing CPU for memory-intensive tasks",
            }

    return None


# Performance rules organized by service
PERFORMANCE_RULES: List[Dict[str, Any]] = [
    # EC2 Rules
    {
        "id": "PERF_EC2_001",
        "title": "EC2 Instance Type Optimization",
        "description": "Ensure EC2 instances use current generation instance types for optimal performance and cost efficiency.",
        "category": "Compute",
        "impact": "HIGH",
        "resource_types": ["AWS::EC2::Instance"],
        "check": check_ec2_instance_type,
        "recommendation": "Use current generation instances (t3, m6i, c6i, r6i) for better price-performance ratio.",
        "terraform_example": '''resource "aws_instance" "example" {
  instance_type = "t3.medium"  # or m6i.large for compute-intensive workloads
  # ...
}''',
    },
    {
        "id": "PERF_EC2_002",
        "title": "EBS Optimization",
        "description": "EBS-optimized instances provide dedicated bandwidth for EBS I/O operations.",
        "category": "Compute",
        "impact": "MEDIUM",
        "resource_types": ["AWS::EC2::Instance"],
        "check": check_ec2_ebs_optimization,
        "recommendation": "Enable EBS optimization for instances with significant I/O requirements.",
        "terraform_example": '''resource "aws_instance" "example" {
  ebs_optimized = true
  # ...
}''',
    },
    {
        "id": "PERF_EC2_003",
        "title": "Detailed CloudWatch Monitoring",
        "description": "Detailed monitoring provides 1-minute metrics instead of 5-minute intervals.",
        "category": "Monitoring",
        "impact": "LOW",
        "resource_types": ["AWS::EC2::Instance"],
        "check": check_ec2_detailed_monitoring,
        "recommendation": "Enable detailed monitoring for faster detection of performance issues.",
        "terraform_example": '''resource "aws_instance" "example" {
  monitoring = true
  # ...
}''',
    },
    # RDS Rules
    {
        "id": "PERF_RDS_001",
        "title": "RDS Instance Class Optimization",
        "description": "Use current generation RDS instance classes for improved performance.",
        "category": "Database",
        "impact": "HIGH",
        "resource_types": ["AWS::RDS::DBInstance"],
        "check": check_rds_instance_class,
        "recommendation": "Upgrade to db.m6i, db.r6i, or db.r6g instance classes for better performance.",
        "terraform_example": '''resource "aws_db_instance" "example" {
  instance_class = "db.r6i.large"
  # ...
}''',
    },
    {
        "id": "PERF_RDS_002",
        "title": "RDS Storage Type Optimization",
        "description": "Use gp3 or io1 storage for better I/O performance.",
        "category": "Database",
        "impact": "HIGH",
        "resource_types": ["AWS::RDS::DBInstance"],
        "check": check_rds_storage_type,
        "recommendation": "Use gp3 storage type for cost-effective baseline performance, or io1/io2 for high IOPS requirements.",
        "terraform_example": '''resource "aws_db_instance" "example" {
  storage_type      = "gp3"
  allocated_storage = 100
  iops              = 3000  # Optional: customize IOPS
  # ...
}''',
    },
    {
        "id": "PERF_RDS_003",
        "title": "RDS Performance Insights",
        "description": "Enable Performance Insights for database performance monitoring and tuning.",
        "category": "Monitoring",
        "impact": "MEDIUM",
        "resource_types": ["AWS::RDS::DBInstance"],
        "check": check_rds_performance_insights,
        "recommendation": "Enable Performance Insights to identify database bottlenecks.",
        "terraform_example": '''resource "aws_db_instance" "example" {
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  # ...
}''',
    },
    # DynamoDB Rules
    {
        "id": "PERF_DDB_001",
        "title": "DynamoDB Capacity Mode",
        "description": "Choose the right capacity mode based on workload patterns.",
        "category": "Database",
        "impact": "MEDIUM",
        "resource_types": ["AWS::DynamoDB::Table"],
        "check": check_dynamodb_capacity_mode,
        "recommendation": "Use On-Demand capacity for unpredictable workloads or Provisioned with Auto Scaling for consistent patterns.",
        "terraform_example": '''resource "aws_dynamodb_table" "example" {
  billing_mode = "PAY_PER_REQUEST"  # On-Demand
  # or
  # billing_mode   = "PROVISIONED"
  # read_capacity  = 10
  # write_capacity = 10
}''',
    },
    {
        "id": "PERF_DDB_002",
        "title": "DynamoDB Auto Scaling",
        "description": "Configure auto scaling for Provisioned capacity mode.",
        "category": "Database",
        "impact": "MEDIUM",
        "resource_types": ["AWS::DynamoDB::Table"],
        "check": check_dynamodb_auto_scaling,
        "recommendation": "Configure Application Auto Scaling policies for DynamoDB tables.",
        "terraform_example": '''resource "aws_appautoscaling_target" "dynamodb_table_read_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/${aws_dynamodb_table.example.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_table_read_policy" {
  name               = "DynamoDBReadCapacityUtilization"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_table_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_table_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_table_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70
  }
}''',
    },
    # Lambda Rules
    {
        "id": "PERF_LAMBDA_001",
        "title": "Lambda Memory Configuration",
        "description": "Lambda CPU allocation scales with memory. Increasing memory can improve performance.",
        "category": "Compute",
        "impact": "HIGH",
        "resource_types": ["AWS::Lambda::Function"],
        "check": check_lambda_memory,
        "recommendation": "Profile your function and adjust memory to optimize performance vs cost.",
        "terraform_example": '''resource "aws_lambda_function" "example" {
  memory_size = 512  # Adjust based on profiling
  # ...
}''',
    },
    {
        "id": "PERF_LAMBDA_002",
        "title": "Lambda Timeout Configuration",
        "description": "Configure appropriate timeout based on function execution time.",
        "category": "Compute",
        "impact": "MEDIUM",
        "resource_types": ["AWS::Lambda::Function"],
        "check": check_lambda_timeout,
        "recommendation": "Set timeout slightly higher than average execution time. For long processes, consider Step Functions.",
        "terraform_example": '''resource "aws_lambda_function" "example" {
  timeout = 30  # Adjust based on execution time
  # ...
}''',
    },
    {
        "id": "PERF_LAMBDA_003",
        "title": "Lambda Cold Start Optimization",
        "description": "Use Provisioned Concurrency for latency-sensitive functions.",
        "category": "Compute",
        "impact": "HIGH",
        "resource_types": ["AWS::Lambda::Function"],
        "check": check_lambda_provisioned_concurrency,
        "recommendation": "Configure Provisioned Concurrency for functions requiring consistent low latency.",
        "terraform_example": '''resource "aws_lambda_provisioned_concurrency_config" "example" {
  function_name                     = aws_lambda_function.example.function_name
  provisioned_concurrent_executions = 5
  qualifier                         = aws_lambda_alias.example.name
}''',
    },
    # S3 Rules
    {
        "id": "PERF_S3_001",
        "title": "S3 Lifecycle Policies",
        "description": "Configure lifecycle policies to optimize storage costs.",
        "category": "Storage",
        "impact": "MEDIUM",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_storage_class,
        "recommendation": "Implement lifecycle rules to transition infrequently accessed data to cheaper storage classes.",
        "terraform_example": '''resource "aws_s3_bucket_lifecycle_configuration" "example" {
  bucket = aws_s3_bucket.example.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}''',
    },
    {
        "id": "PERF_S3_002",
        "title": "S3 Transfer Acceleration",
        "description": "Enable Transfer Acceleration for faster uploads from distant locations.",
        "category": "Storage",
        "impact": "MEDIUM",
        "resource_types": ["AWS::S3::Bucket"],
        "check": check_s3_transfer_acceleration,
        "recommendation": "Enable Transfer Acceleration for buckets accessed from geographically distributed clients.",
        "terraform_example": '''resource "aws_s3_bucket_accelerate_configuration" "example" {
  bucket = aws_s3_bucket.example.id
  status = "Enabled"
}''',
    },
    # ALB Rules
    {
        "id": "PERF_ALB_001",
        "title": "ALB Idle Timeout",
        "description": "Configure appropriate idle timeout for your application.",
        "category": "Networking",
        "impact": "LOW",
        "resource_types": ["AWS::ElasticLoadBalancingV2::LoadBalancer"],
        "check": check_alb_idle_timeout,
        "recommendation": "Set idle timeout based on application requirements. Lower values release connections faster.",
        "terraform_example": '''resource "aws_lb" "example" {
  idle_timeout = 60  # seconds
  # ...
}''',
    },
    # ElastiCache Rules
    {
        "id": "PERF_CACHE_001",
        "title": "ElastiCache Node Type",
        "description": "Use current generation ElastiCache node types for better performance.",
        "category": "Database",
        "impact": "HIGH",
        "resource_types": ["AWS::ElastiCache::CacheCluster", "AWS::ElastiCache::ReplicationGroup"],
        "check": check_elasticache_node_type,
        "recommendation": "Upgrade to r6g or m6g node types for improved performance and Graviton2 benefits.",
        "terraform_example": '''resource "aws_elasticache_cluster" "example" {
  node_type = "cache.r6g.large"
  # ...
}''',
    },
    # CloudFront Rules
    {
        "id": "PERF_CF_001",
        "title": "CloudFront Caching Configuration",
        "description": "Optimize CloudFront caching for better performance and reduced origin load.",
        "category": "CDN",
        "impact": "HIGH",
        "resource_types": ["AWS::CloudFront::Distribution"],
        "check": check_cloudfront_caching,
        "recommendation": "Configure appropriate cache TTLs and cache policies based on content type.",
        "terraform_example": '''resource "aws_cloudfront_cache_policy" "example" {
  name        = "optimized-caching"
  default_ttl = 86400
  max_ttl     = 31536000
  min_ttl     = 1

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "none"
    }
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}''',
    },
    # API Gateway Rules
    {
        "id": "PERF_APIGW_001",
        "title": "API Gateway Caching",
        "description": "Enable caching for frequently accessed API endpoints.",
        "category": "API",
        "impact": "MEDIUM",
        "resource_types": ["AWS::ApiGateway::Stage"],
        "check": check_api_gateway_caching,
        "recommendation": "Enable API Gateway caching to reduce backend load and improve response times.",
        "terraform_example": '''resource "aws_api_gateway_stage" "example" {
  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"  # GB
  # ...
}''',
    },
    # ECS Rules
    {
        "id": "PERF_ECS_001",
        "title": "ECS Task Resource Allocation",
        "description": "Properly size ECS task CPU and memory resources.",
        "category": "Containers",
        "impact": "MEDIUM",
        "resource_types": ["AWS::ECS::TaskDefinition"],
        "check": check_ecs_resource_allocation,
        "recommendation": "Balance CPU and memory allocation based on workload requirements.",
        "terraform_example": '''resource "aws_ecs_task_definition" "example" {
  cpu    = "512"
  memory = "1024"

  container_definitions = jsonencode([{
    cpu    = 256
    memory = 512
    # ...
  }])
}''',
    },
]


def get_rules_for_resource_type(resource_type: str) -> List[Dict[str, Any]]:
    """Get all performance rules applicable to a resource type."""
    return [
        rule for rule in PERFORMANCE_RULES
        if resource_type in rule.get("resource_types", [])
    ]


def get_rules_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all performance rules in a specific category."""
    return [
        rule for rule in PERFORMANCE_RULES
        if rule.get("category") == category
    ]


def get_rules_by_impact(impact: str) -> List[Dict[str, Any]]:
    """Get all performance rules with specific impact level."""
    return [
        rule for rule in PERFORMANCE_RULES
        if rule.get("impact") == impact
    ]
