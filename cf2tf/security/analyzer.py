"""
Security Analyzer

Analyzes CloudFormation resources for security issues based on
Checkov rules and AWS security best practices.
"""

from typing import Any, Dict, List, Optional

from cf2tf.security.rules import SECURITY_RULES, get_rules_for_resource_type


class SecurityAnalyzer:
    """
    Analyzes CloudFormation resources for security vulnerabilities and
    misconfigurations based on Checkov rules and AWS best practices.
    """

    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the security analyzer.

        Args:
            custom_rules: Optional list of custom security rules to add
        """
        self.rules = SECURITY_RULES.copy()
        if custom_rules:
            self.rules.extend(custom_rules)

    def analyze(
        self,
        resources: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze CloudFormation resources for security issues.

        Args:
            resources: CloudFormation Resources section
            parameters: CloudFormation Parameters section (for context)

        Returns:
            List of security findings
        """
        findings = []

        for resource_name, resource_data in resources.items():
            resource_type = resource_data.get("Type", "")
            properties = resource_data.get("Properties", {})

            # Get applicable rules for this resource type
            applicable_rules = get_rules_for_resource_type(resource_type)

            for rule in applicable_rules:
                try:
                    # Run the security check
                    check_func = rule.get("check")
                    if check_func and check_func(properties):
                        findings.append({
                            "check_id": rule.get("id"),
                            "title": rule.get("title"),
                            "description": rule.get("description"),
                            "severity": rule.get("severity"),
                            "resource": resource_name,
                            "resource_type": resource_type,
                            "recommendation": rule.get("recommendation"),
                            "terraform_fix": rule.get("terraform_fix"),
                            "references": rule.get("references", []),
                        })
                except Exception as e:
                    # Log but don't fail on individual rule check errors
                    findings.append({
                        "check_id": rule.get("id"),
                        "title": f"Error checking {rule.get('title')}",
                        "description": f"Error during security check: {str(e)}",
                        "severity": "INFO",
                        "resource": resource_name,
                        "resource_type": resource_type,
                    })

        # Sort findings by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        findings.sort(key=lambda x: severity_order.get(x.get("severity", "INFO"), 5))

        return findings

    def get_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of security findings.

        Args:
            findings: List of security findings

        Returns:
            Summary dictionary with counts by severity and resource
        """
        total = len(findings)
        by_severity: Dict[str, int] = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
        }
        by_resource: Dict[str, int] = {}
        by_check: Dict[str, int] = {}

        for finding in findings:
            severity: str = finding.get("severity", "INFO")
            resource: str = finding.get("resource", "unknown")
            check_id: str = finding.get("check_id", "unknown")

            by_severity[severity] = by_severity.get(severity, 0) + 1

            if resource not in by_resource:
                by_resource[resource] = 0
            by_resource[resource] += 1

            if check_id not in by_check:
                by_check[check_id] = 0
            by_check[check_id] += 1

        return {
            "total": total,
            "by_severity": by_severity,
            "by_resource": by_resource,
            "by_check": by_check,
        }

    def filter_findings(
        self,
        findings: List[Dict[str, Any]],
        min_severity: str = "LOW",
        resource_types: Optional[List[str]] = None,
        exclude_checks: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter findings based on criteria.

        Args:
            findings: List of security findings
            min_severity: Minimum severity level to include
            resource_types: Only include findings for these resource types
            exclude_checks: Check IDs to exclude

        Returns:
            Filtered list of findings
        """
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        min_severity_level = severity_order.get(min_severity, 3)

        filtered = []
        for finding in findings:
            severity = finding.get("severity", "INFO")
            severity_level = severity_order.get(severity, 4)

            # Check severity
            if severity_level > min_severity_level:
                continue

            # Check resource type
            if resource_types and finding.get("resource_type") not in resource_types:
                continue

            # Check excluded checks
            if exclude_checks and finding.get("check_id") in exclude_checks:
                continue

            filtered.append(finding)

        return filtered

    def generate_report(
        self,
        findings: List[Dict[str, Any]],
        format: str = "text",
    ) -> str:
        """
        Generate a formatted report of security findings.

        Args:
            findings: List of security findings
            format: Output format ("text", "json", "markdown")

        Returns:
            Formatted report string
        """
        if format == "json":
            import json
            return json.dumps(findings, indent=2)

        if format == "markdown":
            return self._generate_markdown_report(findings)

        return self._generate_text_report(findings)

    def _generate_text_report(self, findings: List[Dict[str, Any]]) -> str:
        """Generate a plain text report."""
        lines = [
            "=" * 80,
            "SECURITY ANALYSIS REPORT",
            "=" * 80,
            "",
        ]

        summary = self.get_summary(findings)
        lines.extend([
            f"Total Findings: {summary['total']}",
            f"  Critical: {summary['by_severity']['CRITICAL']}",
            f"  High: {summary['by_severity']['HIGH']}",
            f"  Medium: {summary['by_severity']['MEDIUM']}",
            f"  Low: {summary['by_severity']['LOW']}",
            f"  Info: {summary['by_severity']['INFO']}",
            "",
            "-" * 80,
            "DETAILED FINDINGS",
            "-" * 80,
            "",
        ])

        for finding in findings:
            lines.extend([
                f"[{finding.get('severity')}] {finding.get('title')}",
                f"  Check ID: {finding.get('check_id')}",
                f"  Resource: {finding.get('resource')} ({finding.get('resource_type')})",
                f"  Description: {finding.get('description')}",
                f"  Recommendation: {finding.get('recommendation')}",
                "",
            ])

        return "\n".join(lines)

    def _generate_markdown_report(self, findings: List[Dict[str, Any]]) -> str:
        """Generate a Markdown report."""
        lines = [
            "# Security Analysis Report",
            "",
        ]

        summary = self.get_summary(findings)
        lines.extend([
            "## Summary",
            "",
            f"- **Total Findings:** {summary['total']}",
            f"- **Critical:** {summary['by_severity']['CRITICAL']}",
            f"- **High:** {summary['by_severity']['HIGH']}",
            f"- **Medium:** {summary['by_severity']['MEDIUM']}",
            f"- **Low:** {summary['by_severity']['LOW']}",
            "",
            "## Findings",
            "",
        ])

        current_severity = None
        for finding in findings:
            severity = finding.get("severity")
            if severity != current_severity:
                lines.append(f"### {severity}")
                lines.append("")
                current_severity = severity

            lines.extend([
                f"#### {finding.get('title')}",
                "",
                f"- **Check ID:** `{finding.get('check_id')}`",
                f"- **Resource:** `{finding.get('resource')}` (`{finding.get('resource_type')}`)",
                "",
                finding.get("description", ""),
                "",
                "**Recommendation:**",
                finding.get("recommendation", ""),
                "",
            ])

            if finding.get("terraform_fix"):
                lines.extend([
                    "**Terraform Fix:**",
                    "```hcl",
                    finding.get("terraform_fix"),
                    "```",
                    "",
                ])

            lines.append("---")
            lines.append("")

        return "\n".join(lines)


class CheckovIntegration:
    """
    Integration with Checkov for additional security scanning.

    This class provides methods to run Checkov against generated Terraform
    code and parse the results.
    """

    @staticmethod
    def run_checkov(terraform_dir: str, output_format: str = "json") -> Dict[str, Any]:
        """
        Run Checkov against a Terraform directory.

        Args:
            terraform_dir: Path to the directory containing Terraform files
            output_format: Output format (json, cli, etc.)

        Returns:
            Dictionary containing Checkov results
        """
        import subprocess
        import json

        try:
            result = subprocess.run(
                [
                    "checkov",
                    "-d", terraform_dir,
                    "-o", output_format,
                    "--compact",
                ],
                capture_output=True,
                text=True,
            )

            if output_format == "json":
                return json.loads(result.stdout)
            return {"raw_output": result.stdout}

        except FileNotFoundError:
            return {
                "error": "Checkov not found. Install with: pip install checkov",
                "passed": [],
                "failed": [],
            }
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse Checkov output",
                "raw_output": result.stdout,
            }

    @staticmethod
    def parse_checkov_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Checkov results into a standardized format.

        Args:
            results: Raw Checkov results

        Returns:
            List of findings in standardized format
        """
        findings = []

        if "error" in results:
            return findings

        for check_type in results.get("results", {}).get("failed_checks", []):
            findings.append({
                "check_id": check_type.get("check_id"),
                "title": check_type.get("check_name"),
                "description": check_type.get("description", ""),
                "severity": CheckovIntegration._map_checkov_severity(
                    check_type.get("severity", "UNKNOWN")
                ),
                "resource": check_type.get("resource"),
                "file": check_type.get("file_path"),
                "line": check_type.get("file_line_range"),
                "guideline": check_type.get("guideline"),
            })

        return findings

    @staticmethod
    def _map_checkov_severity(severity: str) -> str:
        """Map Checkov severity to standard severity."""
        mapping = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW",
            "INFO": "INFO",
            "UNKNOWN": "INFO",
        }
        return mapping.get(severity.upper(), "INFO")
