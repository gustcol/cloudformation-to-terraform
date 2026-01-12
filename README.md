# CF2TF - CloudFormation to Terraform Migration Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive enterprise-grade framework to migrate AWS CloudFormation templates to Terraform, with built-in security analysis based on Checkov rules, compliance checks (SOC2, HIPAA, PCI-DSS), performance optimization recommendations, and production-ready CI/CD pipelines.

## Features

### Core Capabilities
- **Complete Template Conversion**: Convert CloudFormation YAML/JSON templates to Terraform HCL
- **666+ Resource Types Supported**: 616 AWS resources + 50 Databricks resources
- **Security Analysis**: 88 security checks based on Checkov rules and AWS best practices
- **Compliance Frameworks**: SOC2, HIPAA, PCI-DSS control validation
- **Performance Recommendations**: Actionable performance optimization suggestions

### Enterprise Features
- **Terraform Backend Generator**: S3 + DynamoDB state management with KMS encryption
- **Import Command Generator**: Generate `terraform import` commands or Terraform 1.5+ import blocks
- **Enterprise Tagging Strategy**: Cost allocation, compliance, and operations tags
- **CI/CD Pipeline Templates**: GitHub Actions, GitLab CI, AWS CodePipeline
- **Databricks Provider Support**: Full Databricks on AWS resource mappings
- **User Data Templates**: 18 templates for EC2 instance customization

### Template Features
- **Intrinsic Function Support**: Handles Ref, GetAtt, Sub, Join, If, and more
- **Parameter to Variable Conversion**: Automatic conversion of CloudFormation parameters
- **Output Conversion**: Converts CloudFormation outputs to Terraform outputs
- **Validation**: Template validation before conversion

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Resource Coverage](#resource-coverage)
- [Security Analysis](#security-analysis)
- [Compliance Frameworks](#compliance-frameworks)
- [Terraform Backend Configuration](#terraform-backend-configuration)
- [CI/CD Pipelines](#cicd-pipelines)
- [Tagging Strategy](#tagging-strategy)
- [Databricks Support](#databricks-support)
- [User Data Templates](#user-data-templates)
- [Python API](#python-api)
- [CLI Usage](#cli-usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/gustcol/cloudformation-to-terraform.git
cd cloudformation-to-terraform

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

### Using pip (when published)

```bash
pip install cf2tf
```

### Requirements

- Python 3.8 or higher
- Dependencies (automatically installed):
  - pyyaml
  - click
  - jinja2
  - boto3
  - checkov
  - colorama
  - tabulate

## Quick Start

### Basic Conversion

```bash
# Convert a CloudFormation template to Terraform
cf2tf convert my-template.yaml

# Output will be in ./terraform_output/
```

### With Security Analysis

```bash
cf2tf convert my-template.yaml --security
```

### With Performance Analysis

```bash
cf2tf convert my-template.yaml --performance
```

## Resource Coverage

### Summary

| Provider | Resources | Services |
|----------|-----------|----------|
| **AWS** | 616 | 167 |
| **Databricks** | 50 | 10 categories |
| **Total** | **666** | |

### AWS Services Covered

#### Compute & Networking (78+ resources)
- EC2 (instances, security groups, VPC, subnets, NAT gateways)
- Transit Gateway (14 resources - complete coverage)
- Client VPN, Site-to-Site VPN
- IPAM, Traffic Mirror, Network Insights
- Auto Scaling, Lambda, ECS, EKS

#### Data Analytics (50+ resources)
- **AWS Glue**: 17 resources (Database, Table, Crawler, Job, Connection, Trigger, Workflow, Registry, Schema, etc.)
- **Lake Formation**: 7 resources (Resource, Permissions, DataLakeSettings, Tag, etc.)
- **Athena**: 4 resources (WorkGroup, NamedQuery, DataCatalog, PreparedStatement)
- **EMR**: 8 resources (Cluster, Studio, SecurityConfiguration, etc.)
- **Kinesis**: 10 resources (Stream, Firehose, Analytics v1/v2)
- **MSK**: 6 resources (Cluster, ServerlessCluster, Configuration, etc.)
- **Redshift + Serverless**: 15 resources

#### Search & AI (15+ resources)
- **OpenSearch**: Domain + 6 Serverless resources
- **Amazon Bedrock**: 7 resources (Agent, KnowledgeBase, Guardrail, etc.)
- **SageMaker**: 8 resources

#### Security (50+ resources)
- IAM (9 resources)
- KMS, Secrets Manager
- WAF, WAFv2, WAF Regional (37 resources)
- Shield, Firewall Manager
- VPC Lattice (10 resources)
- Verified Access (4 resources)
- Security Lake (4 resources)

#### Database (25+ resources)
- RDS, Aurora
- DynamoDB
- ElastiCache
- DocumentDB
- Neptune

[View full resource list in docs/RESOURCE_COVERAGE.md](docs/RESOURCE_COVERAGE.md)

## Security Analysis

CF2TF includes **88 security checks** based on Checkov rules and AWS best practices.

### Security Check Categories

| Category | Checks |
|----------|--------|
| S3 | Public access, encryption, versioning, logging |
| EC2/VPC | IMDSv2, EBS encryption, security groups |
| RDS | Encryption, public access, backups, Multi-AZ |
| IAM | Wildcard permissions, admin access, MFA |
| Lambda | VPC config, tracing, environment encryption |
| OpenSearch | Encryption, node-to-node encryption, fine-grained access |
| Bedrock | Guardrail configuration |
| VPC Lattice | Auth policy, resource policy |
| Kinesis | Encryption at rest |

### Example Security Finding

```
[CRITICAL] Security Group SSH Open to World
  Check ID: CKV_AWS_24
  Resource: WebServerSecurityGroup (AWS::EC2::SecurityGroup)
  Description: Security group should not have SSH (port 22) open to 0.0.0.0/0.

  Recommendation: Restrict SSH access to specific IP ranges or use AWS
  Systems Manager Session Manager.
```

## Compliance Frameworks

CF2TF includes compliance controls for major regulatory frameworks:

### Supported Frameworks

| Framework | Controls | Description |
|-----------|----------|-------------|
| **SOC 2 Type II** | 4 | Logical access, encryption, monitoring, change management |
| **HIPAA** | 5 | Technical safeguards (164.312) |
| **PCI-DSS** | 5 | Network segmentation, encryption, audit trails |

### Using Compliance Checks

```python
from cf2tf.compliance import ComplianceChecker, ComplianceFramework

checker = ComplianceChecker(frameworks=[
    ComplianceFramework.SOC2,
    ComplianceFramework.HIPAA,
    ComplianceFramework.PCI_DSS,
])

findings = checker.check_resource(resource_type, resource_config)
report = checker.generate_compliance_report(findings)
```

### Generate Terraform Compliance Controls

```python
# Generate AWS Config rules, GuardDuty, Security Hub, CloudTrail
terraform_code = checker.generate_terraform_controls()
```

## Terraform Backend Configuration

Generate production-ready S3 + DynamoDB backend with encryption:

```python
from cf2tf.terraform import BackendGenerator

backend = BackendGenerator(
    project_name="my-project",
    environment="prod",
    aws_region="us-east-1",
)

# Generate backend configuration
backend_config = backend.generate_s3_backend(
    encrypt=True,
    kms_key_id="alias/terraform-state",
)

# Generate Terraform to create backend infrastructure
infrastructure = backend.generate_backend_resources_tf(
    enable_replication=True,
    replication_region="us-west-2",
)
```

### Features
- S3 bucket with versioning and lifecycle policies
- DynamoDB table for state locking
- KMS encryption for state files
- Cross-region replication for DR
- Bucket policies enforcing TLS and encryption

## CI/CD Pipelines

### GitHub Actions

```python
from cf2tf.cicd import GitHubActionsGenerator

generator = GitHubActionsGenerator()

# Generate complete Terraform CI/CD workflow
workflow = generator.generate_terraform_workflow(
    environments=["dev", "staging", "prod"],
    enable_security_scan=True,      # Checkov, tfsec, Trivy
    enable_cost_estimation=True,    # Infracost integration
    require_approval=True,          # Manual approval for prod
)

# Generate drift detection workflow
drift_workflow = generator.generate_drift_detection_workflow(
    schedule="0 6 * * *",  # Daily at 6 AM
)
```

### GitLab CI

```python
from cf2tf.cicd import PipelineGenerator

gitlab_ci = PipelineGenerator.generate_gitlab_ci(
    environments=["dev", "staging", "prod"],
    terraform_version="1.5.0",
)
```

### AWS CodePipeline

```python
codepipeline_tf = PipelineGenerator.generate_aws_codepipeline()
```

### Pipeline Features
- Terraform validation (fmt, validate, tflint)
- Security scanning (Checkov, tfsec, Trivy)
- Cost estimation (Infracost)
- Multi-environment deployment
- Manual approval gates
- Drift detection
- SARIF report upload for GitHub Security

## Tagging Strategy

Enterprise tagging for cost allocation, compliance, and operations:

```python
from cf2tf.terraform.tagging import TaggingStrategy

tagging = TaggingStrategy(
    project_name="my-project",
    environment="prod",
    owner="platform-team",
    cost_center="engineering",
)

# Get base tags for all resources
tags = tagging.get_base_tags()

# Generate Terraform locals for tagging
terraform_locals = tagging.generate_terraform_locals()

# Generate AWS Config rules for tag compliance
config_rules = tagging.generate_aws_config_rules()

# Generate Cost and Usage Report configuration
cur_config = tagging.generate_cost_allocation_report()
```

### Tag Categories
- **Cost Allocation**: Project, Environment, CostCenter, Owner
- **Operations**: ManagedBy, CreatedDate, BackupPolicy, AutoShutdown
- **Security**: DataClassification, Compliance, SecurityZone
- **Automation**: AutoScale, PatchGroup, MaintenanceWindow

## Databricks Support

Full support for Databricks resources using the databricks/databricks provider:

```python
from cf2tf.resource_mappings import (
    get_databricks_mapping,
    is_databricks_resource,
    get_databricks_provider_block,
)

# Check if resource is Databricks
is_databricks_resource("Custom::DatabricksCluster")  # True

# Get Terraform mapping
get_databricks_mapping("Custom::DatabricksCluster")  # "databricks_cluster"

# Get provider configuration
provider_config = get_databricks_provider_block()
```

### Databricks Resources (50)
| Category | Resources |
|----------|-----------|
| Workspace Management | 7 (MWS workspaces, networks, credentials) |
| Compute | 5 (clusters, jobs, instance pools, pipelines) |
| SQL | 4 (SQL endpoints, queries, dashboards) |
| Unity Catalog | 9 (metastore, catalog, schema, grants) |
| Security | 7 (secrets, tokens, permissions) |
| MLflow & AI | 6 (experiments, models, vector search) |

## User Data Templates

18 templates for EC2 instance customization:

```python
from cf2tf.userdata import UserDataGenerator, list_templates

# List available templates
templates = list_templates()

# Generate user data
generator = UserDataGenerator()
generator.add_template("base-amazon-linux-2")
generator.add_template("webserver-nginx")
generator.add_template("monitoring-cloudwatch-agent")
generator.add_template("security-hardening-base")

user_data = generator.generate()

# Or generate for common scenarios
from cf2tf.userdata.generator import create_userdata_for_scenario

user_data = create_userdata_for_scenario(
    "web_server",
    os="amazon-linux-2",
    server="nginx",
    monitoring=True,
    security_hardening=True,
)
```

### Available Templates
- **Base OS**: amazon-linux-2, ubuntu
- **Web Servers**: nginx, apache
- **Containers**: docker, kubernetes-node
- **Monitoring**: cloudwatch-agent, prometheus-node-exporter
- **Databases**: mysql, postgresql
- **Security**: hardening-base, fail2ban

## Python API

### Basic Usage

```python
from cf2tf import CloudFormationConverter

converter = CloudFormationConverter(
    enable_security_analysis=True,
    enable_performance_analysis=True,
)

result = converter.convert_file(
    file_path="my-template.yaml",
    output_path="./terraform_output",
)

print(result.terraform_code)
print(f"Security findings: {len(result.security_findings)}")
print(f"Performance recommendations: {len(result.performance_recommendations)}")
```

### Import Existing Resources

```python
from cf2tf.terraform import ImportGenerator
from cf2tf.resource_mappings import RESOURCE_TYPE_MAPPING

importer = ImportGenerator()

# From CloudFormation stack resources
importer.from_cloudformation_stack(
    stack_resources=stack_resources,
    resource_mapping=RESOURCE_TYPE_MAPPING,
)

# Generate import commands
import_script = importer.generate_import_commands()

# Or generate Terraform 1.5+ import blocks
import_blocks = importer.generate_import_blocks()
```

## CLI Usage

```bash
# Convert template
cf2tf convert my-template.yaml -o ./terraform_output

# Security analysis only
cf2tf security my-template.yaml --format markdown

# Performance analysis only
cf2tf performance my-template.yaml --min-impact HIGH

# List supported resources
cf2tf supported-resources --filter Glue

# Validate template
cf2tf validate my-template.yaml
```

## Project Structure

```
cf2tf/
├── converter.py           # Main converter
├── resource_mappings/
│   ├── aws_mappings.py    # 616 AWS resources
│   └── databricks_mappings.py  # 50 Databricks resources
├── security/
│   ├── analyzer.py        # Security analyzer
│   └── rules.py           # 88 security rules
├── performance/
│   └── analyzer.py        # Performance analyzer
├── compliance/
│   └── frameworks.py      # SOC2, HIPAA, PCI-DSS
├── terraform/
│   ├── backend.py         # Backend & import generator
│   └── tagging.py         # Tagging strategy
├── cicd/
│   └── github_actions.py  # CI/CD pipelines
└── userdata/
    ├── generator.py       # User data generator
    └── templates.py       # 18 templates
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run type check: `uvx ty check cf2tf/`
6. Submit a pull request

### Adding New Resource Mappings

Edit `cf2tf/resource_mappings/aws_mappings.py`:

```python
RESOURCE_TYPE_MAPPING["AWS::NewService::Resource"] = "aws_new_resource"
```

### Adding Security Rules

Edit `cf2tf/security/rules.py` and add a new rule dictionary to `SECURITY_RULES`.

### Adding Compliance Controls

Edit `cf2tf/compliance/frameworks.py` and add controls to the appropriate framework list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Checkov](https://www.checkov.io/) for security policy inspiration
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)
- [Terraform Databricks Provider](https://registry.terraform.io/providers/databricks/databricks/)

## Support

- **Issues**: [GitHub Issues](https://github.com/gustcol/cloudformation-to-terraform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gustcol/cloudformation-to-terraform/discussions)
- **Documentation**: [docs/RESOURCE_COVERAGE.md](docs/RESOURCE_COVERAGE.md)

---

Made with care for the AWS and Terraform community
