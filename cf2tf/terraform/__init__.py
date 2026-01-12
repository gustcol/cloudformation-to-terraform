"""
Terraform Configuration Module

Provides utilities for generating production-ready Terraform configurations:
- Backend configuration (S3 + DynamoDB)
- Import command generation
- Provider configurations
- Workspace strategies
"""

from cf2tf.terraform.backend import (
    BackendGenerator,
    ImportGenerator,
    PROVIDER_CONFIGURATIONS,
)

__all__ = [
    "BackendGenerator",
    "ImportGenerator",
    "PROVIDER_CONFIGURATIONS",
]
