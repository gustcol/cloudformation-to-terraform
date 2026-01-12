"""
Performance Analyzer

Analyzes CloudFormation resources for performance optimization opportunities.
"""

from typing import Any, Dict, List, Optional

from cf2tf.performance.rules import PERFORMANCE_RULES, get_rules_for_resource_type


class PerformanceAnalyzer:
    """
    Analyzes CloudFormation resources for performance optimization
    opportunities and provides actionable recommendations.
    """

    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the performance analyzer.

        Args:
            custom_rules: Optional list of custom performance rules to add
        """
        self.rules = PERFORMANCE_RULES.copy()
        if custom_rules:
            self.rules.extend(custom_rules)

    def analyze(
        self,
        resources: Dict[str, Any],
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze CloudFormation resources for performance improvements.

        Args:
            resources: CloudFormation Resources section
            parameters: CloudFormation Parameters section (for context)

        Returns:
            List of performance recommendations
        """
        recommendations = []

        for resource_name, resource_data in resources.items():
            resource_type = resource_data.get("Type", "")
            properties = resource_data.get("Properties", {})

            # Get applicable rules for this resource type
            applicable_rules = get_rules_for_resource_type(resource_type)

            for rule in applicable_rules:
                try:
                    # Run the performance check
                    check_func = rule.get("check")
                    if check_func:
                        result = check_func(properties)
                        if result:
                            recommendations.append({
                                "rule_id": rule.get("id"),
                                "title": rule.get("title"),
                                "description": rule.get("description"),
                                "category": rule.get("category"),
                                "impact": rule.get("impact"),
                                "resource": resource_name,
                                "resource_type": resource_type,
                                "issue": result.get("issue"),
                                "current_value": result.get("current"),
                                "suggestion": result.get("suggestion"),
                                "recommendation": rule.get("recommendation"),
                                "terraform_example": rule.get("terraform_example"),
                            })
                except Exception as e:
                    # Log but don't fail on individual rule check errors
                    pass

        # Sort recommendations by impact
        impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: impact_order.get(x.get("impact", "LOW"), 3))

        return recommendations

    def get_summary(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get a summary of performance recommendations.

        Args:
            recommendations: List of performance recommendations

        Returns:
            Summary dictionary with counts by impact and category
        """
        total = len(recommendations)
        by_impact: Dict[str, int] = {
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        by_category: Dict[str, int] = {}
        by_resource: Dict[str, int] = {}

        for rec in recommendations:
            impact: str = rec.get("impact", "LOW")
            category: str = rec.get("category", "General")
            resource: str = rec.get("resource", "unknown")

            by_impact[impact] = by_impact.get(impact, 0) + 1

            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1

            if resource not in by_resource:
                by_resource[resource] = 0
            by_resource[resource] += 1

        return {
            "total": total,
            "by_impact": by_impact,
            "by_category": by_category,
            "by_resource": by_resource,
        }

    def filter_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        min_impact: str = "LOW",
        categories: Optional[List[str]] = None,
        resource_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter recommendations based on criteria.

        Args:
            recommendations: List of performance recommendations
            min_impact: Minimum impact level to include
            categories: Only include recommendations for these categories
            resource_types: Only include recommendations for these resource types

        Returns:
            Filtered list of recommendations
        """
        impact_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        min_impact_level = impact_order.get(min_impact, 2)

        filtered = []
        for rec in recommendations:
            impact = rec.get("impact", "LOW")
            impact_level = impact_order.get(impact, 2)

            # Check impact
            if impact_level > min_impact_level:
                continue

            # Check category
            if categories and rec.get("category") not in categories:
                continue

            # Check resource type
            if resource_types and rec.get("resource_type") not in resource_types:
                continue

            filtered.append(rec)

        return filtered

    def generate_report(
        self,
        recommendations: List[Dict[str, Any]],
        format: str = "text",
    ) -> str:
        """
        Generate a formatted report of performance recommendations.

        Args:
            recommendations: List of performance recommendations
            format: Output format ("text", "json", "markdown")

        Returns:
            Formatted report string
        """
        if format == "json":
            import json
            return json.dumps(recommendations, indent=2)

        if format == "markdown":
            return self._generate_markdown_report(recommendations)

        return self._generate_text_report(recommendations)

    def _generate_text_report(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate a plain text report."""
        lines = [
            "=" * 80,
            "PERFORMANCE ANALYSIS REPORT",
            "=" * 80,
            "",
        ]

        summary = self.get_summary(recommendations)
        lines.extend([
            f"Total Recommendations: {summary['total']}",
            f"  High Impact: {summary['by_impact']['HIGH']}",
            f"  Medium Impact: {summary['by_impact']['MEDIUM']}",
            f"  Low Impact: {summary['by_impact']['LOW']}",
            "",
            "By Category:",
        ])

        for category, count in summary["by_category"].items():
            lines.append(f"  {category}: {count}")

        lines.extend([
            "",
            "-" * 80,
            "DETAILED RECOMMENDATIONS",
            "-" * 80,
            "",
        ])

        for rec in recommendations:
            lines.extend([
                f"[{rec.get('impact')}] {rec.get('title')}",
                f"  Rule ID: {rec.get('rule_id')}",
                f"  Category: {rec.get('category')}",
                f"  Resource: {rec.get('resource')} ({rec.get('resource_type')})",
                f"  Issue: {rec.get('issue')}",
                f"  Current Value: {rec.get('current_value', 'N/A')}",
                f"  Recommendation: {rec.get('recommendation')}",
                "",
            ])

        return "\n".join(lines)

    def _generate_markdown_report(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate a Markdown report."""
        lines = [
            "# Performance Analysis Report",
            "",
        ]

        summary = self.get_summary(recommendations)
        lines.extend([
            "## Summary",
            "",
            f"- **Total Recommendations:** {summary['total']}",
            f"- **High Impact:** {summary['by_impact']['HIGH']}",
            f"- **Medium Impact:** {summary['by_impact']['MEDIUM']}",
            f"- **Low Impact:** {summary['by_impact']['LOW']}",
            "",
            "### By Category",
            "",
        ])

        for category, count in summary["by_category"].items():
            lines.append(f"- **{category}:** {count}")

        lines.extend([
            "",
            "## Recommendations",
            "",
        ])

        current_category = None
        for rec in recommendations:
            category = rec.get("category")
            if category != current_category:
                lines.append(f"### {category}")
                lines.append("")
                current_category = category

            lines.extend([
                f"#### {rec.get('title')} ({rec.get('impact')} Impact)",
                "",
                f"- **Rule ID:** `{rec.get('rule_id')}`",
                f"- **Resource:** `{rec.get('resource')}` (`{rec.get('resource_type')}`)",
                f"- **Issue:** {rec.get('issue')}",
            ])

            if rec.get("current_value"):
                lines.append(f"- **Current Value:** `{rec.get('current_value')}`")

            lines.extend([
                "",
                rec.get("description", ""),
                "",
                "**Recommendation:**",
                rec.get("recommendation", ""),
                "",
            ])

            if rec.get("terraform_example"):
                lines.extend([
                    "**Example Configuration:**",
                    "```hcl",
                    rec.get("terraform_example"),
                    "```",
                    "",
                ])

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def estimate_cost_impact(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Estimate potential cost impact of recommendations.

        Note: This is a rough estimation and actual savings will vary.

        Args:
            recommendations: List of performance recommendations

        Returns:
            Dictionary with estimated cost impact information
        """
        estimates = {
            "potential_savings": [],
            "potential_costs": [],
            "neutral": [],
        }

        # Categorize recommendations by cost impact
        savings_rules = {
            "PERF_EC2_001": "Instance rightsizing can reduce costs by 20-40%",
            "PERF_RDS_002": "gp3 storage is typically 20% cheaper than gp2",
            "PERF_S3_001": "Lifecycle policies can reduce storage costs by 50-70%",
            "PERF_LAMBDA_001": "Right-sized memory can reduce costs",
            "PERF_DDB_001": "On-Demand may be cheaper for variable workloads",
        }

        cost_rules = {
            "PERF_EC2_002": "EBS optimization may incur additional costs on some instances",
            "PERF_EC2_003": "Detailed monitoring costs $3.50/instance/month",
            "PERF_RDS_003": "Performance Insights costs extra",
            "PERF_LAMBDA_003": "Provisioned Concurrency incurs costs even when idle",
            "PERF_S3_002": "Transfer Acceleration costs $0.04-0.08/GB",
        }

        for rec in recommendations:
            rule_id = rec.get("rule_id")

            if rule_id in savings_rules:
                estimates["potential_savings"].append({
                    "rule_id": rule_id,
                    "resource": rec.get("resource"),
                    "estimate": savings_rules[rule_id],
                })
            elif rule_id in cost_rules:
                estimates["potential_costs"].append({
                    "rule_id": rule_id,
                    "resource": rec.get("resource"),
                    "estimate": cost_rules[rule_id],
                })
            else:
                estimates["neutral"].append({
                    "rule_id": rule_id,
                    "resource": rec.get("resource"),
                    "note": "Performance improvement with minimal cost impact",
                })

        return estimates
