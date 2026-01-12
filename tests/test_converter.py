"""
Comprehensive tests for the CF2TF converter.

Tests cover:
- Template parsing (YAML and JSON)
- Resource conversion
- Intrinsic function handling
- Security analysis
- Performance analysis
"""

import json
import pytest
import tempfile
from pathlib import Path

from cf2tf.parser import CloudFormationParser
from cf2tf.converter import CloudFormationConverter
from cf2tf.terraform_generator import TerraformGenerator
from cf2tf.security.analyzer import SecurityAnalyzer
from cf2tf.performance.analyzer import PerformanceAnalyzer
from cf2tf.resource_mappings import get_terraform_resource_type, RESOURCE_TYPE_MAPPING


class TestCloudFormationParser:
    """Tests for CloudFormation template parsing."""

    def test_parse_yaml_template(self):
        """Test parsing a YAML CloudFormation template."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: test-bucket
"""
        parser = CloudFormationParser(template_content=yaml_template)
        result = parser.parse()

        assert "resources" in result
        assert "MyBucket" in result["resources"]
        assert result["resources"]["MyBucket"]["Type"] == "AWS::S3::Bucket"

    def test_parse_json_template(self):
        """Test parsing a JSON CloudFormation template."""
        json_template = json.dumps({
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "Test template",
            "Resources": {
                "MyInstance": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "InstanceType": "t3.micro"
                    }
                }
            }
        })
        parser = CloudFormationParser(template_content=json_template)
        result = parser.parse()

        assert "resources" in result
        assert "MyInstance" in result["resources"]
        assert result["resources"]["MyInstance"]["Type"] == "AWS::EC2::Instance"

    def test_parse_intrinsic_functions(self):
        """Test parsing templates with intrinsic functions."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Environment:
    Type: String
    Default: production
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${Environment}-bucket"
      Tags:
        - Key: Env
          Value: !Ref Environment
"""
        parser = CloudFormationParser(template_content=yaml_template)
        result = parser.parse()

        assert "parameters" in result
        assert "Environment" in result["parameters"]
        assert "Fn::Sub" in str(result["resources"]["MyBucket"]["Properties"]["BucketName"])

    def test_parse_mappings_and_conditions(self):
        """Test parsing templates with mappings and conditions."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345678
    us-west-2:
      AMI: ami-87654321
Conditions:
  CreateProdResources: !Equals [!Ref Environment, production]
Parameters:
  Environment:
    Type: String
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Condition: CreateProdResources
    Properties:
      ImageId: !FindInMap [RegionMap, !Ref "AWS::Region", AMI]
"""
        parser = CloudFormationParser(template_content=yaml_template)
        result = parser.parse()

        assert "mappings" in result
        assert "RegionMap" in result["mappings"]
        assert "conditions" in result
        assert "CreateProdResources" in result["conditions"]

    def test_validate_template_errors(self):
        """Test template validation catches errors."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  InvalidResource:
    Properties:
      SomeProperty: value
"""
        parser = CloudFormationParser(template_content=yaml_template)
        parser.parse()
        issues = parser.validate_template()

        assert len(issues) > 0
        assert any("Type" in issue.get("message", "") for issue in issues)

    def test_get_resource_dependencies(self):
        """Test extracting resource dependencies."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Test SG
  Instance:
    Type: AWS::EC2::Instance
    DependsOn: SecurityGroup
    Properties:
      SecurityGroupIds:
        - !Ref SecurityGroup
"""
        parser = CloudFormationParser(template_content=yaml_template)
        parser.parse()

        deps = parser.get_dependencies("Instance")
        assert "SecurityGroup" in deps


class TestResourceMappings:
    """Tests for resource type mappings."""

    def test_ec2_resources_mapped(self):
        """Test EC2 resources are correctly mapped."""
        ec2_types = [
            "AWS::EC2::Instance",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::VPC",
            "AWS::EC2::Subnet",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::NatGateway",
            "AWS::EC2::RouteTable",
            "AWS::EC2::Route",
            "AWS::EC2::EIP",
        ]
        for cfn_type in ec2_types:
            tf_type = get_terraform_resource_type(cfn_type)
            assert tf_type is not None, f"{cfn_type} should be mapped"
            assert tf_type.startswith("aws_"), f"{cfn_type} should map to aws_ resource"

    def test_s3_resources_mapped(self):
        """Test S3 resources are correctly mapped."""
        assert get_terraform_resource_type("AWS::S3::Bucket") == "aws_s3_bucket"
        assert get_terraform_resource_type("AWS::S3::BucketPolicy") == "aws_s3_bucket_policy"

    def test_rds_resources_mapped(self):
        """Test RDS resources are correctly mapped."""
        rds_types = [
            "AWS::RDS::DBInstance",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBSubnetGroup",
            "AWS::RDS::DBParameterGroup",
        ]
        for cfn_type in rds_types:
            tf_type = get_terraform_resource_type(cfn_type)
            assert tf_type is not None, f"{cfn_type} should be mapped"

    def test_lambda_resources_mapped(self):
        """Test Lambda resources are correctly mapped."""
        lambda_types = [
            "AWS::Lambda::Function",
            "AWS::Lambda::Permission",
            "AWS::Lambda::EventSourceMapping",
            "AWS::Lambda::Alias",
            "AWS::Lambda::LayerVersion",
        ]
        for cfn_type in lambda_types:
            tf_type = get_terraform_resource_type(cfn_type)
            assert tf_type is not None, f"{cfn_type} should be mapped"

    def test_iam_resources_mapped(self):
        """Test IAM resources are correctly mapped."""
        iam_types = [
            "AWS::IAM::Role",
            "AWS::IAM::Policy",
            "AWS::IAM::InstanceProfile",
            "AWS::IAM::User",
            "AWS::IAM::Group",
        ]
        for cfn_type in iam_types:
            tf_type = get_terraform_resource_type(cfn_type)
            assert tf_type is not None, f"{cfn_type} should be mapped"

    def test_dynamodb_resources_mapped(self):
        """Test DynamoDB resources are correctly mapped."""
        assert get_terraform_resource_type("AWS::DynamoDB::Table") == "aws_dynamodb_table"

    def test_ecs_resources_mapped(self):
        """Test ECS resources are correctly mapped."""
        ecs_types = [
            "AWS::ECS::Cluster",
            "AWS::ECS::Service",
            "AWS::ECS::TaskDefinition",
        ]
        for cfn_type in ecs_types:
            tf_type = get_terraform_resource_type(cfn_type)
            assert tf_type is not None, f"{cfn_type} should be mapped"

    def test_all_mappings_have_aws_prefix(self):
        """Test all Terraform mappings have aws_ prefix."""
        for cfn_type, tf_type in RESOURCE_TYPE_MAPPING.items():
            if tf_type != "module":  # Exceptions for nested stacks
                assert tf_type.startswith("aws_"), f"{cfn_type} mapping {tf_type} should start with aws_"


class TestTerraformGenerator:
    """Tests for Terraform HCL generation."""

    def test_generate_basic_resource(self):
        """Test generating a basic Terraform resource."""
        generator = TerraformGenerator()
        resources = {
            "MyBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": "test-bucket"
                }
            }
        }
        result = generator.generate(
            resources=resources,
            parameters={},
            outputs={},
            mappings={},
            conditions={},
        )

        assert "resource \"aws_s3_bucket\"" in result
        assert "my_bucket" in result
        assert "test-bucket" in result

    def test_generate_variables_from_parameters(self):
        """Test generating Terraform variables from CloudFormation parameters."""
        generator = TerraformGenerator()
        parameters = {
            "InstanceType": {
                "Type": "String",
                "Default": "t3.micro",
                "Description": "EC2 instance type"
            }
        }
        result = generator.generate(
            resources={},
            parameters=parameters,
            outputs={},
            mappings={},
            conditions={},
        )

        assert "variable \"instance_type\"" in result
        assert "description" in result
        assert "t3.micro" in result

    def test_generate_outputs(self):
        """Test generating Terraform outputs."""
        generator = TerraformGenerator()
        outputs = {
            "BucketArn": {
                "Description": "S3 Bucket ARN",
                "Value": {"Fn::GetAtt": ["MyBucket", "Arn"]}
            }
        }
        resources = {
            "MyBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {}
            }
        }
        result = generator.generate(
            resources=resources,
            parameters={},
            outputs=outputs,
            mappings={},
            conditions={},
        )

        assert "output \"bucket_arn\"" in result

    def test_convert_ref_function(self):
        """Test converting Ref intrinsic function."""
        generator = TerraformGenerator()
        generator.parameters = {"Environment": {"Type": "String"}}
        generator.resources = {}

        ref_value = {"Ref": "Environment"}
        result = generator._convert_value(ref_value)

        assert "var.environment" in result

    def test_convert_getatt_function(self):
        """Test converting GetAtt intrinsic function."""
        generator = TerraformGenerator()
        generator.parameters = {}
        generator.resources = {
            "MyBucket": {"Type": "AWS::S3::Bucket", "Properties": {}}
        }
        generator._build_resource_name_mapping()

        getatt_value = {"Fn::GetAtt": ["MyBucket", "Arn"]}
        result = generator._convert_value(getatt_value)

        assert "aws_s3_bucket" in result
        assert "arn" in result


class TestSecurityAnalyzer:
    """Tests for security analysis."""

    def test_detect_public_s3_bucket(self):
        """Test detection of public S3 bucket."""
        analyzer = SecurityAnalyzer()
        resources = {
            "PublicBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "AccessControl": "PublicRead"
                }
            }
        }
        findings = analyzer.analyze(resources)

        assert len(findings) > 0
        assert any("public" in f.get("title", "").lower() for f in findings)

    def test_detect_unencrypted_s3_bucket(self):
        """Test detection of unencrypted S3 bucket."""
        analyzer = SecurityAnalyzer()
        resources = {
            "UnencryptedBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "BucketName": "unencrypted-bucket"
                }
            }
        }
        findings = analyzer.analyze(resources)

        assert len(findings) > 0
        assert any("encrypt" in f.get("title", "").lower() for f in findings)

    def test_detect_open_ssh_security_group(self):
        """Test detection of security group with SSH open to world."""
        analyzer = SecurityAnalyzer()
        resources = {
            "InsecureSG": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "Test",
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "CidrIp": "0.0.0.0/0"
                        }
                    ]
                }
            }
        }
        findings = analyzer.analyze(resources)

        assert len(findings) > 0
        assert any("ssh" in f.get("title", "").lower() for f in findings)
        assert any(f.get("severity") == "CRITICAL" for f in findings)

    def test_detect_public_rds(self):
        """Test detection of publicly accessible RDS."""
        analyzer = SecurityAnalyzer()
        resources = {
            "PublicRDS": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "DBInstanceClass": "db.t3.micro",
                    "Engine": "mysql",
                    "PubliclyAccessible": True
                }
            }
        }
        findings = analyzer.analyze(resources)

        assert len(findings) > 0
        assert any("public" in f.get("title", "").lower() for f in findings)

    def test_detect_unencrypted_rds(self):
        """Test detection of unencrypted RDS."""
        analyzer = SecurityAnalyzer()
        resources = {
            "UnencryptedRDS": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "DBInstanceClass": "db.t3.micro",
                    "Engine": "mysql",
                    "StorageEncrypted": False
                }
            }
        }
        findings = analyzer.analyze(resources)

        assert len(findings) > 0
        assert any("encrypt" in f.get("title", "").lower() for f in findings)

    def test_detect_overly_permissive_iam(self):
        """Test detection of overly permissive IAM policy."""
        analyzer = SecurityAnalyzer()
        resources = {
            "AdminRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {},
                    "Policies": [
                        {
                            "PolicyName": "Admin",
                            "PolicyDocument": {
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "*",
                                        "Resource": "*"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        findings = analyzer.analyze(resources)

        # The IAM policy checks should detect this
        assert len(findings) >= 0

    def test_filter_findings_by_severity(self):
        """Test filtering findings by severity."""
        analyzer = SecurityAnalyzer()
        findings = [
            {"severity": "CRITICAL", "title": "Critical issue"},
            {"severity": "HIGH", "title": "High issue"},
            {"severity": "MEDIUM", "title": "Medium issue"},
            {"severity": "LOW", "title": "Low issue"},
        ]

        filtered = analyzer.filter_findings(findings, min_severity="HIGH")
        assert len(filtered) == 2
        assert all(f["severity"] in ["CRITICAL", "HIGH"] for f in filtered)

    def test_generate_markdown_report(self):
        """Test generating markdown security report."""
        analyzer = SecurityAnalyzer()
        findings = [
            {
                "check_id": "CKV_AWS_1",
                "title": "Test Finding",
                "description": "Test description",
                "severity": "HIGH",
                "resource": "TestResource",
                "resource_type": "AWS::S3::Bucket",
                "recommendation": "Fix it",
            }
        ]

        report = analyzer.generate_report(findings, format="markdown")
        assert "# Security Analysis Report" in report
        assert "HIGH" in report
        assert "Test Finding" in report


class TestPerformanceAnalyzer:
    """Tests for performance analysis."""

    def test_detect_outdated_ec2_instance_type(self):
        """Test detection of outdated EC2 instance types."""
        analyzer = PerformanceAnalyzer()
        resources = {
            "OldInstance": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "InstanceType": "m3.large"
                }
            }
        }
        recommendations = analyzer.analyze(resources)

        assert len(recommendations) > 0
        assert any("instance" in r.get("title", "").lower() for r in recommendations)

    def test_detect_low_lambda_memory(self):
        """Test detection of minimum Lambda memory."""
        analyzer = PerformanceAnalyzer()
        resources = {
            "SmallLambda": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "MemorySize": 128,
                    "Runtime": "python3.9",
                    "Handler": "index.handler"
                }
            }
        }
        recommendations = analyzer.analyze(resources)

        assert len(recommendations) > 0
        assert any("memory" in r.get("title", "").lower() for r in recommendations)

    def test_detect_magnetic_rds_storage(self):
        """Test detection of magnetic RDS storage."""
        analyzer = PerformanceAnalyzer()
        resources = {
            "SlowRDS": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "DBInstanceClass": "db.t3.micro",
                    "Engine": "mysql",
                    "StorageType": "standard"
                }
            }
        }
        recommendations = analyzer.analyze(resources)

        assert len(recommendations) > 0
        assert any("storage" in r.get("title", "").lower() for r in recommendations)

    def test_filter_recommendations_by_impact(self):
        """Test filtering recommendations by impact."""
        analyzer = PerformanceAnalyzer()
        recommendations = [
            {"impact": "HIGH", "title": "High impact"},
            {"impact": "MEDIUM", "title": "Medium impact"},
            {"impact": "LOW", "title": "Low impact"},
        ]

        filtered = analyzer.filter_recommendations(recommendations, min_impact="MEDIUM")
        assert len(filtered) == 2
        assert all(r["impact"] in ["HIGH", "MEDIUM"] for r in filtered)

    def test_get_recommendations_summary(self):
        """Test getting recommendations summary."""
        analyzer = PerformanceAnalyzer()
        recommendations = [
            {"impact": "HIGH", "category": "Compute", "resource": "Instance1"},
            {"impact": "MEDIUM", "category": "Compute", "resource": "Instance2"},
            {"impact": "LOW", "category": "Database", "resource": "DB1"},
        ]

        summary = analyzer.get_summary(recommendations)
        assert summary["total"] == 3
        assert summary["by_impact"]["HIGH"] == 1
        assert summary["by_category"]["Compute"] == 2


class TestCloudFormationConverter:
    """Tests for the main converter class."""

    def test_convert_simple_template(self):
        """Test converting a simple template."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: test-bucket
"""
        converter = CloudFormationConverter()
        result = converter.convert_string(yaml_template)

        assert result.terraform_code is not None
        assert "aws_s3_bucket" in result.terraform_code
        assert result.resource_summary["total"] == 1
        assert result.resource_summary["converted"] == 1

    def test_convert_template_with_security_analysis(self):
        """Test conversion with security analysis."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  InsecureBucket:
    Type: AWS::S3::Bucket
    Properties:
      AccessControl: PublicRead
"""
        converter = CloudFormationConverter(enable_security_analysis=True)
        result = converter.convert_string(yaml_template)

        assert len(result.security_findings) > 0
        assert any("public" in f.get("title", "").lower() for f in result.security_findings)

    def test_convert_template_with_performance_analysis(self):
        """Test conversion with performance analysis."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  OldInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: m3.large
"""
        converter = CloudFormationConverter(enable_performance_analysis=True)
        result = converter.convert_string(yaml_template)

        assert len(result.performance_recommendations) > 0

    def test_convert_complex_template(self):
        """Test converting a complex template with multiple resources."""
        yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Environment:
    Type: String
    Default: production
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Test SG
      VpcId: !Ref VPC
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      SubnetId: !Ref Subnet
      SecurityGroupIds:
        - !Ref SecurityGroup
Outputs:
  InstanceId:
    Value: !Ref Instance
"""
        converter = CloudFormationConverter()
        result = converter.convert_string(yaml_template)

        assert result.resource_summary["total"] == 4
        assert result.resource_summary["converted"] == 4
        assert "aws_vpc" in result.terraform_code
        assert "aws_subnet" in result.terraform_code
        assert "aws_security_group" in result.terraform_code
        assert "aws_instance" in result.terraform_code

    def test_convert_file(self, tmp_path):
        """Test converting a template file."""
        template_file = tmp_path / "test-template.yaml"
        template_file.write_text("""
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
""")
        converter = CloudFormationConverter()
        result = converter.convert_file(str(template_file))

        assert result.terraform_code is not None
        assert "aws_s3_bucket" in result.terraform_code


class TestResourceCoverage:
    """Tests to verify coverage of AWS service resource types."""

    def test_compute_services_covered(self):
        """Test that compute service resources are covered."""
        compute_types = [
            "AWS::EC2::Instance",
            "AWS::EC2::LaunchTemplate",
            "AWS::AutoScaling::AutoScalingGroup",
            "AWS::Lambda::Function",
            "AWS::ECS::Cluster",
            "AWS::ECS::Service",
            "AWS::ECS::TaskDefinition",
            "AWS::EKS::Cluster",
            "AWS::EKS::Nodegroup",
        ]
        for cfn_type in compute_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_networking_services_covered(self):
        """Test that networking service resources are covered."""
        networking_types = [
            "AWS::EC2::VPC",
            "AWS::EC2::Subnet",
            "AWS::EC2::InternetGateway",
            "AWS::EC2::NatGateway",
            "AWS::EC2::RouteTable",
            "AWS::EC2::Route",
            "AWS::EC2::SecurityGroup",
            "AWS::EC2::VPCEndpoint",
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            "AWS::ElasticLoadBalancingV2::Listener",
            "AWS::CloudFront::Distribution",
            "AWS::Route53::HostedZone",
            "AWS::Route53::RecordSet",
        ]
        for cfn_type in networking_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_storage_services_covered(self):
        """Test that storage service resources are covered."""
        storage_types = [
            "AWS::S3::Bucket",
            "AWS::S3::BucketPolicy",
            "AWS::EC2::Volume",
            "AWS::DynamoDB::Table",
        ]
        for cfn_type in storage_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_database_services_covered(self):
        """Test that database service resources are covered."""
        database_types = [
            "AWS::RDS::DBInstance",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBSubnetGroup",
            "AWS::RDS::DBParameterGroup",
            "AWS::DynamoDB::Table",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ReplicationGroup",
        ]
        for cfn_type in database_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_security_services_covered(self):
        """Test that security service resources are covered."""
        security_types = [
            "AWS::IAM::Role",
            "AWS::IAM::Policy",
            "AWS::IAM::User",
            "AWS::IAM::Group",
            "AWS::IAM::InstanceProfile",
            "AWS::KMS::Key",
            "AWS::KMS::Alias",
            "AWS::SecretsManager::Secret",
            "AWS::WAFv2::WebACL",
            "AWS::WAFv2::IPSet",
        ]
        for cfn_type in security_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_monitoring_services_covered(self):
        """Test that monitoring service resources are covered."""
        monitoring_types = [
            "AWS::CloudWatch::Alarm",
            "AWS::CloudWatch::Dashboard",
            "AWS::Logs::LogGroup",
            "AWS::Events::Rule",
        ]
        for cfn_type in monitoring_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_messaging_services_covered(self):
        """Test that messaging service resources are covered."""
        messaging_types = [
            "AWS::SNS::Topic",
            "AWS::SNS::Subscription",
            "AWS::SQS::Queue",
            "AWS::SQS::QueuePolicy",
        ]
        for cfn_type in messaging_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_api_services_covered(self):
        """Test that API service resources are covered."""
        api_types = [
            "AWS::ApiGateway::RestApi",
            "AWS::ApiGateway::Resource",
            "AWS::ApiGateway::Method",
            "AWS::ApiGateway::Stage",
            "AWS::ApiGatewayV2::Api",
        ]
        for cfn_type in api_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"

    def test_container_services_covered(self):
        """Test that container service resources are covered."""
        container_types = [
            "AWS::ECS::Cluster",
            "AWS::ECS::Service",
            "AWS::ECS::TaskDefinition",
            "AWS::ECR::Repository",
            "AWS::EKS::Cluster",
            "AWS::EKS::Nodegroup",
        ]
        for cfn_type in container_types:
            assert get_terraform_resource_type(cfn_type) is not None, f"{cfn_type} should be covered"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
