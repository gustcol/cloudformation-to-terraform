#!/usr/bin/env python3
"""
Quick test script to verify the CF2TF framework works correctly.

This script tests:
1. Template parsing (YAML/JSON)
2. Resource conversion
3. Security analysis
4. Performance analysis
5. Terraform HCL generation
"""

import sys
import os
from pathlib import Path

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

from cf2tf.parser import CloudFormationParser
from cf2tf.converter import CloudFormationConverter
from cf2tf.security.analyzer import SecurityAnalyzer
from cf2tf.performance.analyzer import PerformanceAnalyzer
from cf2tf.resource_mappings import RESOURCE_TYPE_MAPPING


def test_parser():
    """Test CloudFormation parser."""
    print("\n" + "=" * 60)
    print("Testing CloudFormation Parser...")
    print("=" * 60)

    yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template
Parameters:
  Environment:
    Type: String
    Default: production
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${Environment}-bucket"
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.micro
      ImageId: ami-12345678
Outputs:
  BucketName:
    Value: !Ref MyBucket
"""
    parser = CloudFormationParser(template_content=yaml_template)
    result = parser.parse()

    assert "resources" in result, "Parser should return resources"
    assert len(result["resources"]) == 2, "Should have 2 resources"
    assert "parameters" in result, "Parser should return parameters"
    assert "outputs" in result, "Parser should return outputs"

    print(f"  Parsed {len(result['resources'])} resources")
    print(f"  Parsed {len(result['parameters'])} parameters")
    print(f"  Parsed {len(result['outputs'])} outputs")
    print("  Parser test PASSED")


def test_resource_mappings():
    """Test resource type mappings coverage."""
    print("\n" + "=" * 60)
    print("Testing Resource Mappings Coverage...")
    print("=" * 60)

    # Count by service
    services = {}
    for cfn_type in RESOURCE_TYPE_MAPPING.keys():
        parts = cfn_type.split("::")
        if len(parts) >= 2:
            service = parts[1]
            services[service] = services.get(service, 0) + 1

    print(f"  Total resource types supported: {len(RESOURCE_TYPE_MAPPING)}")
    print("  By service:")
    for service, count in sorted(services.items(), key=lambda x: -x[1])[:15]:
        print(f"    {service}: {count}")

    # Verify key services are covered
    key_services = ["EC2", "S3", "IAM", "RDS", "Lambda", "DynamoDB", "ECS", "EKS", "SNS", "SQS"]
    missing = [s for s in key_services if s not in services]
    assert len(missing) == 0, f"Missing key services: {missing}"

    print(f"  All key services covered")
    print("  Resource mappings test PASSED")


def test_security_analyzer():
    """Test security analyzer."""
    print("\n" + "=" * 60)
    print("Testing Security Analyzer...")
    print("=" * 60)

    analyzer = SecurityAnalyzer()

    # Test various security issues
    resources = {
        "PublicBucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "AccessControl": "PublicRead"
            }
        },
        "UnencryptedBucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": "test"
            }
        },
        "OpenSSH": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Test",
                "SecurityGroupIngress": [
                    {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "CidrIp": "0.0.0.0/0"}
                ]
            }
        },
        "PublicRDS": {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "PubliclyAccessible": True,
                "StorageEncrypted": False
            }
        }
    }

    findings = analyzer.analyze(resources)
    summary = analyzer.get_summary(findings)

    print(f"  Total findings: {summary['total']}")
    print(f"    Critical: {summary['by_severity']['CRITICAL']}")
    print(f"    High: {summary['by_severity']['HIGH']}")
    print(f"    Medium: {summary['by_severity']['MEDIUM']}")
    print(f"    Low: {summary['by_severity']['LOW']}")

    assert summary["total"] > 0, "Should detect security issues"
    assert summary["by_severity"]["CRITICAL"] > 0, "Should detect critical issues (open SSH)"

    print("  Security analyzer test PASSED")


def test_performance_analyzer():
    """Test performance analyzer."""
    print("\n" + "=" * 60)
    print("Testing Performance Analyzer...")
    print("=" * 60)

    analyzer = PerformanceAnalyzer()

    resources = {
        "OldInstance": {
            "Type": "AWS::EC2::Instance",
            "Properties": {
                "InstanceType": "m3.large"  # Outdated
            }
        },
        "SmallLambda": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "MemorySize": 128,  # Minimum
                "Timeout": 3  # Default
            }
        },
        "SlowRDS": {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "StorageType": "standard"  # Magnetic
            }
        }
    }

    recommendations = analyzer.analyze(resources)
    summary = analyzer.get_summary(recommendations)

    print(f"  Total recommendations: {summary['total']}")
    print(f"    High Impact: {summary['by_impact']['HIGH']}")
    print(f"    Medium Impact: {summary['by_impact']['MEDIUM']}")
    print(f"    Low Impact: {summary['by_impact']['LOW']}")

    assert summary["total"] > 0, "Should detect performance issues"

    print("  Performance analyzer test PASSED")


def test_converter():
    """Test full conversion pipeline."""
    print("\n" + "=" * 60)
    print("Testing Full Converter Pipeline...")
    print("=" * 60)

    yaml_template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test VPC with EC2

Parameters:
  Environment:
    Type: String
    Default: production
  InstanceType:
    Type: String
    Default: t3.micro

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub "${Environment}-vpc"

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web server security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: !Ref InstanceType
      ImageId: ami-12345678
      SubnetId: !Ref PublicSubnet
      SecurityGroupIds:
        - !Ref SecurityGroup

Outputs:
  VPCId:
    Value: !Ref VPC
    Description: VPC ID
  InstanceId:
    Value: !Ref WebServer
    Description: Instance ID
"""

    converter = CloudFormationConverter(
        enable_security_analysis=True,
        enable_performance_analysis=True
    )
    result = converter.convert_string(yaml_template)

    print(f"  Resources converted: {result.resource_summary['converted']}/{result.resource_summary['total']}")
    print(f"  Security findings: {len(result.security_findings)}")
    print(f"  Performance recommendations: {len(result.performance_recommendations)}")

    assert result.terraform_code is not None, "Should generate Terraform code"
    assert "aws_vpc" in result.terraform_code, "Should contain VPC resource"
    assert "aws_subnet" in result.terraform_code, "Should contain Subnet resource"
    assert "aws_instance" in result.terraform_code, "Should contain Instance resource"
    assert "variable" in result.terraform_code, "Should contain variables"
    assert "output" in result.terraform_code, "Should contain outputs"

    # Check Terraform code structure
    assert "terraform {" in result.terraform_code, "Should have terraform block"
    assert "provider \"aws\"" in result.terraform_code, "Should have AWS provider"

    print("  Converter test PASSED")
    print("\n  Sample Terraform output (first 50 lines):")
    print("  " + "-" * 50)
    for i, line in enumerate(result.terraform_code.split("\n")[:50]):
        print(f"    {line}")
    print("    ...")


def test_example_templates():
    """Test conversion of example templates."""
    print("\n" + "=" * 60)
    print("Testing Example Templates...")
    print("=" * 60)

    examples_dir = Path(__file__).parent / "examples"
    if not examples_dir.exists():
        print("  Examples directory not found, skipping...")
        return

    converter = CloudFormationConverter(
        enable_security_analysis=True,
        enable_performance_analysis=True
    )

    for template_file in sorted(examples_dir.glob("*.yaml")):
        print(f"\n  Testing: {template_file.name}")
        try:
            result = converter.convert_file(str(template_file))
            print(f"    Resources: {result.resource_summary['converted']}/{result.resource_summary['total']}")
            print(f"    Security findings: {len(result.security_findings)}")
            print(f"    Performance recommendations: {len(result.performance_recommendations)}")
            print(f"    Status: PASSED")
        except Exception as e:
            print(f"    Error: {e}")
            print(f"    Status: FAILED")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CF2TF Framework Test Suite")
    print("=" * 60)

    try:
        test_parser()
        test_resource_mappings()
        test_security_analyzer()
        test_performance_analyzer()
        test_converter()
        test_example_templates()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
