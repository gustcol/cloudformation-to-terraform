"""
CI/CD Pipeline Templates

Generates production-ready CI/CD pipeline configurations for Terraform deployments.
Supports GitHub Actions, GitLab CI, and AWS CodePipeline.
"""

from typing import Dict, List, Optional


class GitHubActionsGenerator:
    """Generator for GitHub Actions workflows."""

    def generate_terraform_workflow(
        self,
        environments: Optional[List[str]] = None,
        aws_region: str = "us-east-1",
        terraform_version: str = "1.5.0",
        enable_cost_estimation: bool = True,
        enable_security_scan: bool = True,
        require_approval: bool = True,
    ) -> str:
        """
        Generate complete Terraform CI/CD workflow.

        Args:
            environments: List of deployment environments.
            aws_region: AWS region for deployment.
            terraform_version: Terraform version to use.
            enable_cost_estimation: Enable Infracost integration.
            enable_security_scan: Enable security scanning.
            require_approval: Require manual approval for prod.

        Returns:
            GitHub Actions workflow YAML.
        """
        if environments is None:
            environments = ["dev", "staging", "prod"]

        workflow = f'''name: Terraform CI/CD Pipeline

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'terraform/**'
      - '.github/workflows/terraform.yml'
  pull_request:
    branches:
      - main
      - develop
    paths:
      - 'terraform/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod
      action:
        description: 'Action to perform'
        required: true
        type: choice
        options:
          - plan
          - apply
          - destroy

env:
  TF_VERSION: "{terraform_version}"
  AWS_REGION: "{aws_region}"
  TF_IN_AUTOMATION: "true"

permissions:
  id-token: write
  contents: read
  pull-requests: write
  security-events: write

jobs:
  # ==============================================================================
  # Validation Stage
  # ==============================================================================
  validate:
    name: Validate Terraform
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{{{ env.TF_VERSION }}}}

      - name: Terraform Format Check
        id: fmt
        run: terraform fmt -check -recursive
        continue-on-error: true

      - name: Terraform Init
        id: init
        run: terraform init -backend=false
        working-directory: terraform

      - name: Terraform Validate
        id: validate
        run: terraform validate -no-color
        working-directory: terraform

      - name: TFLint
        uses: terraform-linters/setup-tflint@v4
        with:
          tflint_version: latest

      - name: Run TFLint
        run: |
          tflint --init
          tflint --recursive --format=compact
        working-directory: terraform
'''

        if enable_security_scan:
            workflow += '''
  # ==============================================================================
  # Security Scanning Stage
  # ==============================================================================
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: validate
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          output_format: cli,sarif
          output_file_path: console,results.sarif
          soft_fail: true

      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: results.sarif

      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: terraform/
          soft_fail: true

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: 'terraform/'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: trivy-results.sarif
'''

        if enable_cost_estimation:
            workflow += '''
  # ==============================================================================
  # Cost Estimation Stage
  # ==============================================================================
  cost-estimation:
    name: Cost Estimation
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'pull_request'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v2
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Infracost JSON
        run: |
          infracost breakdown --path terraform/ \\
            --format json \\
            --out-file /tmp/infracost-base.json

      - name: Generate Infracost Diff
        run: |
          infracost diff --path terraform/ \\
            --format json \\
            --compare-to /tmp/infracost-base.json \\
            --out-file /tmp/infracost.json

      - name: Post Infracost comment
        uses: infracost/actions/comment@v2
        with:
          path: /tmp/infracost.json
          behavior: update
'''

        # Add plan jobs for each environment
        for env in environments:
            needs = "security-scan" if enable_security_scan else "validate"
            workflow += f'''
  # ==============================================================================
  # Plan Stage - {env.upper()}
  # ==============================================================================
  plan-{env}:
    name: Plan ({env})
    runs-on: ubuntu-latest
    needs: [{needs}]
    if: |
      (github.event_name == 'pull_request') ||
      (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == '{env}')
    environment: {env}-plan
    outputs:
      plan-exitcode: ${{{{ steps.plan.outputs.exitcode }}}}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{{{ secrets.AWS_ROLE_ARN_{env.upper()} }}}}
          aws-region: ${{{{ env.AWS_REGION }}}}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{{{ env.TF_VERSION }}}}

      - name: Terraform Init
        run: terraform init
        working-directory: terraform

      - name: Select Workspace
        run: terraform workspace select {env} || terraform workspace new {env}
        working-directory: terraform

      - name: Terraform Plan
        id: plan
        run: |
          terraform plan -var-file=environments/{env}.tfvars \\
            -out=tfplan-{env} \\
            -detailed-exitcode \\
            -no-color
        working-directory: terraform
        continue-on-error: true

      - name: Upload Plan
        uses: actions/upload-artifact@v4
        with:
          name: tfplan-{env}
          path: terraform/tfplan-{env}
          retention-days: 5

      - name: Comment Plan on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const output = `#### Terraform Plan - {env} 🧱

            \`\`\`
            ${{{{ steps.plan.outputs.stdout }}}}
            \`\`\`

            *Pusher: @${{{{ github.actor }}}}, Action: \`${{{{ github.event_name }}}}\`*`;

            github.rest.issues.createComment({{
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            }})
'''

        # Add apply jobs for each environment
        for i, env in enumerate(environments):
            prev_env = environments[i - 1] if i > 0 else None
            needs_list = [f"plan-{env}"]
            if prev_env and require_approval:
                needs_list.append(f"apply-{prev_env}")

            approval_text = ""
            if env == "prod" and require_approval:
                approval_text = """
    # Requires manual approval for production
"""

            workflow += f'''
  # ==============================================================================
  # Apply Stage - {env.upper()}
  # ==============================================================================
  apply-{env}:
    name: Apply ({env})
    runs-on: ubuntu-latest
    needs: [{", ".join(needs_list)}]
    if: |
      (github.ref == 'refs/heads/main' && github.event_name == 'push') ||
      (github.event_name == 'workflow_dispatch' &&
       github.event.inputs.environment == '{env}' &&
       github.event.inputs.action == 'apply')
    environment: {env}{approval_text}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{{{ secrets.AWS_ROLE_ARN_{env.upper()} }}}}
          aws-region: ${{{{ env.AWS_REGION }}}}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{{{ env.TF_VERSION }}}}

      - name: Terraform Init
        run: terraform init
        working-directory: terraform

      - name: Select Workspace
        run: terraform workspace select {env}
        working-directory: terraform

      - name: Download Plan
        uses: actions/download-artifact@v4
        with:
          name: tfplan-{env}
          path: terraform/

      - name: Terraform Apply
        run: terraform apply -auto-approve tfplan-{env}
        working-directory: terraform

      - name: Terraform Output
        id: output
        run: terraform output -json > outputs-{env}.json
        working-directory: terraform

      - name: Upload Outputs
        uses: actions/upload-artifact@v4
        with:
          name: outputs-{env}
          path: terraform/outputs-{env}.json
'''

        return workflow

    def generate_drift_detection_workflow(
        self,
        environments: Optional[List[str]] = None,
        schedule: str = "0 6 * * *",  # Daily at 6 AM
    ) -> str:
        """
        Generate drift detection workflow.

        Args:
            environments: List of environments to check.
            schedule: Cron schedule for drift detection.

        Returns:
            GitHub Actions workflow YAML.
        """
        if environments is None:
            environments = ["dev", "staging", "prod"]

        workflow = f'''name: Terraform Drift Detection

on:
  schedule:
    - cron: '{schedule}'
  workflow_dispatch:

env:
  TF_VERSION: "1.5.0"
  AWS_REGION: "us-east-1"

permissions:
  id-token: write
  contents: read
  issues: write

jobs:
'''

        for env in environments:
            workflow += f'''
  drift-{env}:
    name: Check Drift ({env})
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{{{ secrets.AWS_ROLE_ARN_{env.upper()} }}}}
          aws-region: ${{{{ env.AWS_REGION }}}}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{{{ env.TF_VERSION }}}}

      - name: Terraform Init
        run: terraform init
        working-directory: terraform

      - name: Select Workspace
        run: terraform workspace select {env}
        working-directory: terraform

      - name: Check for Drift
        id: drift
        run: |
          terraform plan -var-file=environments/{env}.tfvars \\
            -detailed-exitcode \\
            -no-color > drift-report.txt 2>&1 || exitcode=$?

          if [ "$exitcode" == "2" ]; then
            echo "drift=true" >> $GITHUB_OUTPUT
            echo "::warning::Drift detected in {env} environment"
          else
            echo "drift=false" >> $GITHUB_OUTPUT
          fi
        working-directory: terraform
        continue-on-error: true

      - name: Create Issue on Drift
        if: steps.drift.outputs.drift == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const drift = fs.readFileSync('terraform/drift-report.txt', 'utf8');

            github.rest.issues.create({{
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Terraform Drift Detected - {env}',
              body: `## Drift Detection Report

              **Environment:** {env}
              **Detected:** ${{{{ github.event.repository.updated_at }}}}

              ### Changes Detected

              \`\`\`
              ${{drift.substring(0, 60000)}}
              \`\`\`

              ### Action Required

              Please review the changes and either:
              1. Apply the Terraform configuration to correct the drift
              2. Update the Terraform code to match the current state

              /cc @${{{{ github.repository_owner }}}}`,
              labels: ['drift', 'terraform', '{env}']
            }})
'''

        return workflow

    def generate_pr_workflow(self) -> str:
        """
        Generate PR validation workflow.

        Returns:
            GitHub Actions workflow YAML.
        """
        return '''name: PR Validation

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  pr-validation:
    name: Validate PR
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check commit messages
        uses: wagoid/commitlint-github-action@v5

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      - name: Terraform docs check
        uses: terraform-docs/gh-actions@v1
        with:
          working-dir: terraform/
          output-file: README.md
          output-method: inject
          fail-on-diff: true

      - name: Check for large files
        run: |
          find . -type f -size +1M -not -path "./.git/*" | while read file; do
            echo "::warning::Large file detected: $file"
          done
'''


class PipelineGenerator:
    """Generator for various CI/CD pipeline configurations."""

    @staticmethod
    def generate_gitlab_ci(
        environments: Optional[List[str]] = None,
        terraform_version: str = "1.5.0",
    ) -> str:
        """
        Generate GitLab CI pipeline configuration.

        Args:
            environments: List of deployment environments.
            terraform_version: Terraform version to use.

        Returns:
            GitLab CI YAML configuration.
        """
        if environments is None:
            environments = ["dev", "staging", "prod"]

        return f'''# GitLab CI/CD Pipeline for Terraform
# Generated by CF2TF

stages:
  - validate
  - security
  - plan
  - apply

variables:
  TF_VERSION: "{terraform_version}"
  TF_IN_AUTOMATION: "true"

image:
  name: hashicorp/terraform:$TF_VERSION
  entrypoint: [""]

.terraform-init: &terraform-init
  before_script:
    - cd terraform
    - terraform init

validate:
  stage: validate
  <<: *terraform-init
  script:
    - terraform fmt -check -recursive
    - terraform validate
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

security-scan:
  stage: security
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d terraform/ --framework terraform
  allow_failure: true
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
''' + "\n".join([f'''
plan-{env}:
  stage: plan
  <<: *terraform-init
  script:
    - terraform workspace select {env} || terraform workspace new {env}
    - terraform plan -var-file=environments/{env}.tfvars -out=tfplan-{env}
  artifacts:
    paths:
      - terraform/tfplan-{env}
    expire_in: 1 week
  environment:
    name: {env}
    action: prepare
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

apply-{env}:
  stage: apply
  <<: *terraform-init
  script:
    - terraform workspace select {env}
    - terraform apply -auto-approve tfplan-{env}
  dependencies:
    - plan-{env}
  environment:
    name: {env}
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  {"when: manual" if env == "prod" else ""}
''' for env in environments])

    @staticmethod
    def generate_aws_codepipeline() -> str:
        """
        Generate AWS CodePipeline Terraform configuration.

        Returns:
            Terraform configuration for CodePipeline.
        """
        return '''# ==============================================================================
# AWS CodePipeline for Terraform Deployments
# ==============================================================================

resource "aws_codepipeline" "terraform" {
  name     = "${var.project_name}-terraform-pipeline"
  role_arn = aws_iam_role.codepipeline.arn

  artifact_store {
    location = aws_s3_bucket.artifacts.bucket
    type     = "S3"

    encryption_key {
      id   = aws_kms_key.artifacts.arn
      type = "KMS"
    }
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = aws_codestarconnections_connection.github.arn
        FullRepositoryId = var.github_repository
        BranchName       = var.github_branch
      }
    }
  }

  stage {
    name = "Validate"

    action {
      name             = "TerraformValidate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["validate_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.terraform_validate.name
      }
    }
  }

  stage {
    name = "SecurityScan"

    action {
      name             = "Checkov"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["security_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.security_scan.name
      }
    }
  }

  stage {
    name = "Plan"

    action {
      name             = "TerraformPlan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["plan_output"]
      version          = "1"

      configuration = {
        ProjectName = aws_codebuild_project.terraform_plan.name
      }
    }
  }

  stage {
    name = "Approval"

    action {
      name     = "ManualApproval"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
      version  = "1"

      configuration = {
        NotificationArn = aws_sns_topic.approvals.arn
        CustomData      = "Please review the Terraform plan before applying."
      }
    }
  }

  stage {
    name = "Apply"

    action {
      name            = "TerraformApply"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      input_artifacts = ["plan_output"]
      version         = "1"

      configuration = {
        ProjectName = aws_codebuild_project.terraform_apply.name
      }
    }
  }

  tags = local.common_tags
}

# CodeBuild Projects
resource "aws_codebuild_project" "terraform_validate" {
  name          = "${var.project_name}-terraform-validate"
  description   = "Validate Terraform configuration"
  build_timeout = 10
  service_role  = aws_iam_role.codebuild.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "hashicorp/terraform:1.5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOF
      version: 0.2
      phases:
        install:
          commands:
            - terraform --version
        build:
          commands:
            - cd terraform
            - terraform init -backend=false
            - terraform fmt -check -recursive
            - terraform validate
    EOF
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "security_scan" {
  name          = "${var.project_name}-security-scan"
  description   = "Security scan with Checkov"
  build_timeout = 15
  service_role  = aws_iam_role.codebuild.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "bridgecrew/checkov:latest"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOF
      version: 0.2
      phases:
        build:
          commands:
            - checkov -d terraform/ --framework terraform --soft-fail
    EOF
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "terraform_plan" {
  name          = "${var.project_name}-terraform-plan"
  description   = "Generate Terraform plan"
  build_timeout = 30
  service_role  = aws_iam_role.codebuild.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "hashicorp/terraform:1.5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOF
      version: 0.2
      phases:
        build:
          commands:
            - cd terraform
            - terraform init
            - terraform workspace select $ENVIRONMENT || terraform workspace new $ENVIRONMENT
            - terraform plan -var-file=environments/$ENVIRONMENT.tfvars -out=tfplan
      artifacts:
        files:
          - terraform/tfplan
    EOF
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "terraform_apply" {
  name          = "${var.project_name}-terraform-apply"
  description   = "Apply Terraform changes"
  build_timeout = 60
  service_role  = aws_iam_role.codebuild.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "hashicorp/terraform:1.5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "SERVICE_ROLE"
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-EOF
      version: 0.2
      phases:
        build:
          commands:
            - cd terraform
            - terraform init
            - terraform workspace select $ENVIRONMENT
            - terraform apply -auto-approve tfplan
    EOF
  }

  tags = local.common_tags
}
'''
