"""
CF2TF Command Line Interface

Provides a user-friendly CLI for converting CloudFormation templates to Terraform.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from colorama import Fore, Style, init as colorama_init

from cf2tf import __version__
from cf2tf.converter import CloudFormationConverter, ConversionResult


# Initialize colorama for cross-platform colored output
colorama_init()


def print_banner():
    """Print the CF2TF banner."""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗███████╗██████╗ ████████╗███████╗    CloudFormation to Terraform     ║
║  ██╔════╝██╔════╝╚════██╗╚══██╔══╝██╔════╝    Migration Framework             ║
║  ██║     █████╗   █████╔╝   ██║   █████╗      Version {__version__:<24}║
║  ██║     ██╔══╝  ██╔═══╝    ██║   ██╔══╝                                      ║
║  ╚██████╗██║     ███████╗   ██║   ██║         Security + Performance          ║
║   ╚═════╝╚═╝     ╚══════╝   ╚═╝   ╚═╝         Best Practices Built-in         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    click.echo(banner)


def print_success(message: str):
    """Print a success message."""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message."""
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message."""
    click.echo(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def print_section(title: str):
    """Print a section header."""
    click.echo(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")


@click.group()
@click.version_option(version=__version__, prog_name="cf2tf")
def main():
    """
    CF2TF - CloudFormation to Terraform Migration Framework

    Convert AWS CloudFormation templates to Terraform with security
    and performance recommendations.
    """
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output directory for Terraform files (default: ./terraform_output)",
)
@click.option(
    "--security/--no-security",
    default=True,
    help="Enable/disable security analysis (default: enabled)",
)
@click.option(
    "--performance/--no-performance",
    default=True,
    help="Enable/disable performance analysis (default: enabled)",
)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format for reports (default: text)",
)
@click.option(
    "--min-severity",
    type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]),
    default="LOW",
    help="Minimum severity level for security findings (default: LOW)",
)
@click.option(
    "--min-impact",
    type=click.Choice(["HIGH", "MEDIUM", "LOW"]),
    default="LOW",
    help="Minimum impact level for performance recommendations (default: LOW)",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress informational output",
)
@click.option(
    "--stdout",
    is_flag=True,
    help="Output Terraform code to stdout instead of file",
)
def convert(
    input_file: str,
    output: Optional[str],
    security: bool,
    performance: bool,
    format: str,
    min_severity: str,
    min_impact: str,
    quiet: bool,
    stdout: bool,
):
    """
    Convert a CloudFormation template to Terraform.

    INPUT_FILE: Path to the CloudFormation template (YAML or JSON)

    Examples:

        cf2tf convert template.yaml

        cf2tf convert template.yaml -o ./my-terraform

        cf2tf convert template.yaml --no-security --format json
    """
    if not quiet:
        print_banner()

    # Set default output directory
    if not output and not stdout:
        output = "./terraform_output"

    try:
        # Create converter
        converter = CloudFormationConverter(
            enable_security_analysis=security,
            enable_performance_analysis=performance,
        )

        if not quiet:
            print_info(f"Converting: {input_file}")

        # Perform conversion
        result = converter.convert_file(
            file_path=input_file,
            output_path=output if not stdout else None,
        )

        # Output to stdout if requested
        if stdout:
            click.echo(result.terraform_code)
            return

        # Print results
        if not quiet and output:
            _print_conversion_results(result, output, format, min_severity, min_impact)

    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        print_error(f"Invalid template: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Conversion failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--min-severity",
    type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]),
    default="LOW",
    help="Minimum severity level (default: LOW)",
)
def security(input_file: str, format: str, min_severity: str):
    """
    Analyze a CloudFormation template for security issues.

    INPUT_FILE: Path to the CloudFormation template (YAML or JSON)

    Examples:

        cf2tf security template.yaml

        cf2tf security template.yaml --format json

        cf2tf security template.yaml --min-severity HIGH
    """
    print_banner()

    try:
        converter = CloudFormationConverter(
            enable_security_analysis=True,
            enable_performance_analysis=False,
        )

        print_info(f"Analyzing: {input_file}")

        result = converter.convert_file(file_path=input_file)

        # Filter findings
        from cf2tf.security.analyzer import SecurityAnalyzer
        analyzer = SecurityAnalyzer()
        filtered = analyzer.filter_findings(
            result.security_findings,
            min_severity=min_severity,
        )

        # Generate report
        report = analyzer.generate_report(filtered, format=format)
        click.echo(report)

        # Exit with error if critical issues found
        if result.has_critical_security_issues():
            sys.exit(2)

    except Exception as e:
        print_error(f"Analysis failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["text", "json", "markdown"]),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--min-impact",
    type=click.Choice(["HIGH", "MEDIUM", "LOW"]),
    default="LOW",
    help="Minimum impact level (default: LOW)",
)
@click.option(
    "--category",
    multiple=True,
    help="Filter by category (can be specified multiple times)",
)
def performance(input_file: str, format: str, min_impact: str, category: tuple):
    """
    Analyze a CloudFormation template for performance improvements.

    INPUT_FILE: Path to the CloudFormation template (YAML or JSON)

    Examples:

        cf2tf performance template.yaml

        cf2tf performance template.yaml --format markdown

        cf2tf performance template.yaml --category Compute --category Database
    """
    print_banner()

    try:
        converter = CloudFormationConverter(
            enable_security_analysis=False,
            enable_performance_analysis=True,
        )

        print_info(f"Analyzing: {input_file}")

        result = converter.convert_file(file_path=input_file)

        # Filter recommendations
        from cf2tf.performance.analyzer import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        filtered = analyzer.filter_recommendations(
            result.performance_recommendations,
            min_impact=min_impact,
            categories=list(category) if category else None,
        )

        # Generate report
        report = analyzer.generate_report(filtered, format=format)
        click.echo(report)

    except Exception as e:
        print_error(f"Analysis failed: {e}")
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file: str):
    """
    Validate a CloudFormation template.

    INPUT_FILE: Path to the CloudFormation template (YAML or JSON)

    Examples:

        cf2tf validate template.yaml
    """
    print_banner()

    try:
        from cf2tf.parser import CloudFormationParser

        print_info(f"Validating: {input_file}")

        parser = CloudFormationParser(template_path=input_file)
        parser.parse()
        issues = parser.validate_template()

        if not issues:
            print_success("Template is valid!")
            return

        print_warning(f"Found {len(issues)} validation issues:")
        for issue in issues:
            severity = issue.get("severity", "INFO")
            message = issue.get("message", "")
            location = issue.get("location", "")

            if severity == "error":
                print_error(f"  [{location}] {message}")
            else:
                print_warning(f"  [{location}] {message}")

        # Exit with error if there are errors
        if any(i.get("severity") == "error" for i in issues):
            sys.exit(1)

    except Exception as e:
        print_error(f"Validation failed: {e}")
        sys.exit(1)


@main.command(name="list-resources")
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format (default: text)",
)
def list_resources(input_file: str, format: str):
    """
    List all resources in a CloudFormation template.

    INPUT_FILE: Path to the CloudFormation template (YAML or JSON)

    Examples:

        cf2tf list-resources template.yaml

        cf2tf list-resources template.yaml --format json
    """
    try:
        from cf2tf.parser import CloudFormationParser
        from cf2tf.resource_mappings import get_terraform_resource_type

        parser = CloudFormationParser(template_path=input_file)
        parsed = parser.parse()

        resources = []
        for name, data in parsed["resources"].items():
            cfn_type = data.get("Type", "Unknown")
            tf_type = get_terraform_resource_type(cfn_type)
            resources.append({
                "name": name,
                "cfn_type": cfn_type,
                "tf_type": tf_type or "NOT SUPPORTED",
                "supported": tf_type is not None,
            })

        if format == "json":
            click.echo(json.dumps(resources, indent=2))
        else:
            print_section("Resources")
            supported = sum(1 for r in resources if r["supported"])
            click.echo(f"\nTotal: {len(resources)} | Supported: {supported} | Unsupported: {len(resources) - supported}\n")

            for r in resources:
                status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if r["supported"] else f"{Fore.RED}✗{Style.RESET_ALL}"
                click.echo(f"{status} {r['name']}")
                click.echo(f"    CloudFormation: {r['cfn_type']}")
                click.echo(f"    Terraform:      {r['tf_type']}")
                click.echo()

    except Exception as e:
        print_error(f"Failed to list resources: {e}")
        sys.exit(1)


@main.command(name="supported-resources")
@click.option(
    "--filter",
    help="Filter resources by keyword (e.g., 'EC2', 'Lambda')",
)
def supported_resources(filter: Optional[str]):
    """
    List all supported CloudFormation resource types.

    Examples:

        cf2tf supported-resources

        cf2tf supported-resources --filter EC2
    """
    from cf2tf.resource_mappings import RESOURCE_TYPE_MAPPING

    print_section("Supported Resource Types")

    mappings = RESOURCE_TYPE_MAPPING.items()
    if filter:
        mappings = [(k, v) for k, v in mappings if filter.upper() in k.upper()]

    click.echo(f"\nTotal: {len(list(mappings))} resource types\n")

    for cfn_type, tf_type in sorted(mappings):
        click.echo(f"{Fore.CYAN}{cfn_type}{Style.RESET_ALL}")
        click.echo(f"  → {tf_type}")


def _print_conversion_results(
    result: ConversionResult,
    output_dir: str,
    format: str,
    min_severity: str,
    min_impact: str,
):
    """Print conversion results to console."""
    # Resource summary
    print_section("Resource Summary")
    summary = result.resource_summary
    click.echo(f"\nTotal Resources: {summary['total']}")
    click.echo(f"  Converted: {Fore.GREEN}{summary['converted']}{Style.RESET_ALL}")
    click.echo(f"  Unsupported: {Fore.YELLOW}{summary['unsupported']}{Style.RESET_ALL}")

    if summary["unsupported"] > 0:
        click.echo(f"\n{Fore.YELLOW}Unsupported resource types:{Style.RESET_ALL}")
        for rtype, info in summary["by_type"].items():
            if not info["supported"]:
                click.echo(f"  - {rtype} ({info['count']})")

    # Security findings
    if result.security_findings:
        print_section("Security Findings")
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for finding in result.security_findings:
            severity_counts[finding.get("severity", "INFO")] += 1

        click.echo(f"\n{Fore.RED}Critical: {severity_counts['CRITICAL']}{Style.RESET_ALL}")
        click.echo(f"{Fore.RED}High: {severity_counts['HIGH']}{Style.RESET_ALL}")
        click.echo(f"{Fore.YELLOW}Medium: {severity_counts['MEDIUM']}{Style.RESET_ALL}")
        click.echo(f"Low: {severity_counts['LOW']}")
        click.echo(f"Info: {severity_counts['INFO']}")

        if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0:
            print_warning("\nPlease review SECURITY_FINDINGS.md for critical issues!")

    # Performance recommendations
    if result.performance_recommendations:
        print_section("Performance Recommendations")
        impact_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for rec in result.performance_recommendations:
            impact_counts[rec.get("impact", "LOW")] += 1

        click.echo(f"\n{Fore.RED}High Impact: {impact_counts['HIGH']}{Style.RESET_ALL}")
        click.echo(f"{Fore.YELLOW}Medium Impact: {impact_counts['MEDIUM']}{Style.RESET_ALL}")
        click.echo(f"Low Impact: {impact_counts['LOW']}")

    # Output files
    print_section("Output Files")
    output_path = Path(output_dir)
    click.echo(f"\n{Fore.GREEN}✓{Style.RESET_ALL} {output_path / 'main.tf'}")

    if result.security_findings:
        click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} {output_path / 'SECURITY_FINDINGS.md'}")

    if result.performance_recommendations:
        click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} {output_path / 'PERFORMANCE_RECOMMENDATIONS.md'}")

    print_success(f"\nConversion completed successfully!")
    print_info(f"Next steps:")
    click.echo(f"  1. cd {output_dir}")
    click.echo(f"  2. terraform init")
    click.echo(f"  3. terraform plan")
    click.echo(f"  4. Review and apply changes")


if __name__ == "__main__":
    main()
