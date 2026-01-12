"""
CloudFormation to Terraform Converter

Main orchestrator that combines parsing, conversion, security analysis,
and performance recommendations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cf2tf.parser import CloudFormationParser
from cf2tf.terraform_generator import TerraformGenerator
from cf2tf.security.analyzer import SecurityAnalyzer
from cf2tf.performance.analyzer import PerformanceAnalyzer


class ConversionResult:
    """Container for conversion results."""

    def __init__(
        self,
        terraform_code: str,
        security_findings: List[Dict[str, Any]],
        performance_recommendations: List[Dict[str, Any]],
        conversion_warnings: List[Dict[str, Any]],
        resource_summary: Dict[str, Any],
    ):
        self.terraform_code = terraform_code
        self.security_findings = security_findings
        self.performance_recommendations = performance_recommendations
        self.conversion_warnings = conversion_warnings
        self.resource_summary = resource_summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "terraform_code": self.terraform_code,
            "security_findings": self.security_findings,
            "performance_recommendations": self.performance_recommendations,
            "conversion_warnings": self.conversion_warnings,
            "resource_summary": self.resource_summary,
        }

    def has_critical_security_issues(self) -> bool:
        """Check if there are critical security issues."""
        return any(
            finding.get("severity") == "CRITICAL"
            for finding in self.security_findings
        )

    def has_high_security_issues(self) -> bool:
        """Check if there are high severity security issues."""
        return any(
            finding.get("severity") in ["CRITICAL", "HIGH"]
            for finding in self.security_findings
        )


class CloudFormationConverter:
    """
    Main converter class that orchestrates the CloudFormation to Terraform conversion.

    Features:
    - Parses CloudFormation templates (YAML/JSON)
    - Converts resources to Terraform HCL
    - Analyzes security based on Checkov rules and best practices
    - Provides performance recommendations
    """

    def __init__(
        self,
        enable_security_analysis: bool = True,
        enable_performance_analysis: bool = True,
    ):
        """
        Initialize the converter.

        Args:
            enable_security_analysis: Enable security findings and recommendations
            enable_performance_analysis: Enable performance recommendations
        """
        self.enable_security_analysis = enable_security_analysis
        self.enable_performance_analysis = enable_performance_analysis
        self.parser: Optional[CloudFormationParser] = None
        self.generator = TerraformGenerator()
        self.security_analyzer = SecurityAnalyzer() if enable_security_analysis else None
        self.performance_analyzer = PerformanceAnalyzer() if enable_performance_analysis else None

    def convert_file(self, file_path: str, output_path: Optional[str] = None) -> ConversionResult:
        """
        Convert a CloudFormation template file to Terraform.

        Args:
            file_path: Path to the CloudFormation template file
            output_path: Optional path to write the Terraform output

        Returns:
            ConversionResult containing the Terraform code and analysis results
        """
        self.parser = CloudFormationParser(template_path=file_path)
        return self._convert(output_path)

    def convert_string(self, template_content: str, output_path: Optional[str] = None) -> ConversionResult:
        """
        Convert a CloudFormation template string to Terraform.

        Args:
            template_content: CloudFormation template as string
            output_path: Optional path to write the Terraform output

        Returns:
            ConversionResult containing the Terraform code and analysis results
        """
        self.parser = CloudFormationParser(template_content=template_content)
        return self._convert(output_path)

    def _convert(self, output_path: Optional[str] = None) -> ConversionResult:
        """
        Internal conversion method.

        Args:
            output_path: Optional path to write the Terraform output

        Returns:
            ConversionResult containing all conversion outputs
        """
        # Ensure parser is initialized
        if self.parser is None:
            raise RuntimeError("Parser not initialized. Use convert_file() or convert_string() instead.")

        # Parse the template
        parsed = self.parser.parse()

        # Validate the template
        validation_issues = self.parser.validate_template()
        conversion_warnings = [
            {"type": "validation", **issue} for issue in validation_issues
        ]

        # Generate Terraform code
        terraform_code = self.generator.generate(
            resources=parsed["resources"],
            parameters=parsed["parameters"],
            outputs=parsed["outputs"],
            mappings=parsed["mappings"],
            conditions=parsed["conditions"],
        )

        # Track unsupported resources
        resource_summary = self._get_resource_summary(parsed["resources"])

        # Security analysis
        security_findings = []
        if self.security_analyzer:
            security_findings = self.security_analyzer.analyze(
                parsed["resources"],
                parsed["parameters"],
            )

        # Performance analysis
        performance_recommendations = []
        if self.performance_analyzer:
            performance_recommendations = self.performance_analyzer.analyze(
                parsed["resources"],
                parsed["parameters"],
            )

        # Write output if path provided
        if output_path:
            self._write_output(output_path, terraform_code, security_findings, performance_recommendations)

        return ConversionResult(
            terraform_code=terraform_code,
            security_findings=security_findings,
            performance_recommendations=performance_recommendations,
            conversion_warnings=conversion_warnings,
            resource_summary=resource_summary,
        )

    def _get_resource_summary(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of resources by type."""
        from cf2tf.resource_mappings import get_terraform_resource_type

        total = len(resources)
        converted = 0
        unsupported = 0
        by_type: Dict[str, Dict[str, Any]] = {}

        for name, resource in resources.items():
            cfn_type: str = resource.get("Type", "Unknown")

            if cfn_type not in by_type:
                by_type[cfn_type] = {"count": 0, "supported": False}

            by_type[cfn_type]["count"] += 1

            if get_terraform_resource_type(cfn_type):
                converted += 1
                by_type[cfn_type]["supported"] = True
            else:
                unsupported += 1

        return {
            "total": total,
            "converted": converted,
            "unsupported": unsupported,
            "by_type": by_type,
        }

    def _write_output(
        self,
        output_path: str,
        terraform_code: str,
        security_findings: List[Dict[str, Any]],
        performance_recommendations: List[Dict[str, Any]],
    ):
        """Write conversion output to files."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write main Terraform file
        main_tf = output_dir / "main.tf"
        main_tf.write_text(terraform_code)

        # Write security findings
        if security_findings:
            security_file = output_dir / "SECURITY_FINDINGS.md"
            security_content = self._format_security_findings(security_findings)
            security_file.write_text(security_content)

        # Write performance recommendations
        if performance_recommendations:
            perf_file = output_dir / "PERFORMANCE_RECOMMENDATIONS.md"
            perf_content = self._format_performance_recommendations(performance_recommendations)
            perf_file.write_text(perf_content)

    def _format_security_findings(self, findings: List[Dict[str, Any]]) -> str:
        """Format security findings as Markdown."""
        lines = [
            "# Security Findings",
            "",
            "The following security issues were identified during conversion.",
            "Please review and address these findings before deploying.",
            "",
        ]

        # Group by severity
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        findings_by_severity = {s: [] for s in severity_order}

        for finding in findings:
            severity = finding.get("severity", "INFO")
            findings_by_severity.get(severity, findings_by_severity["INFO"]).append(finding)

        for severity in severity_order:
            severity_findings = findings_by_severity[severity]
            if not severity_findings:
                continue

            lines.append(f"## {severity} Severity ({len(severity_findings)})")
            lines.append("")

            for finding in severity_findings:
                lines.append(f"### {finding.get('title', 'Untitled')}")
                lines.append("")
                lines.append(f"**Resource:** {finding.get('resource', 'N/A')}")
                lines.append(f"**Check ID:** {finding.get('check_id', 'N/A')}")
                lines.append("")
                lines.append(finding.get("description", ""))
                lines.append("")
                if finding.get("recommendation"):
                    lines.append("**Recommendation:**")
                    lines.append(finding.get("recommendation"))
                    lines.append("")
                if finding.get("terraform_fix"):
                    lines.append("**Terraform Fix:**")
                    lines.append("```hcl")
                    lines.append(finding.get("terraform_fix"))
                    lines.append("```")
                    lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _format_performance_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format performance recommendations as Markdown."""
        lines = [
            "# Performance Recommendations",
            "",
            "The following performance optimizations are recommended for your infrastructure.",
            "",
        ]

        # Group by category
        by_category = {}
        for rec in recommendations:
            category = rec.get("category", "General")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(rec)

        for category, recs in by_category.items():
            lines.append(f"## {category}")
            lines.append("")

            for rec in recs:
                lines.append(f"### {rec.get('title', 'Untitled')}")
                lines.append("")
                lines.append(f"**Resource:** {rec.get('resource', 'N/A')}")
                lines.append(f"**Impact:** {rec.get('impact', 'N/A')}")
                lines.append("")
                lines.append(rec.get("description", ""))
                lines.append("")
                if rec.get("recommendation"):
                    lines.append("**Recommendation:**")
                    lines.append(rec.get("recommendation"))
                    lines.append("")
                if rec.get("terraform_example"):
                    lines.append("**Example Configuration:**")
                    lines.append("```hcl")
                    lines.append(rec.get("terraform_example"))
                    lines.append("```")
                    lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)
