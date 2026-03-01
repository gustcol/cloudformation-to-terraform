"""
CF2TF - CloudFormation to Terraform Migration Framework

A comprehensive framework to migrate AWS CloudFormation templates to Terraform
with security recommendations based on best practices and Checkov,
plus performance optimization suggestions.
"""

__version__ = "1.1.0"
__author__ = "CF2TF Team"

from cf2tf.converter import CloudFormationConverter
from cf2tf.parser import CloudFormationParser
from cf2tf.terraform_generator import TerraformGenerator

__all__ = [
    "CloudFormationConverter",
    "CloudFormationParser",
    "TerraformGenerator",
    "__version__",
]
