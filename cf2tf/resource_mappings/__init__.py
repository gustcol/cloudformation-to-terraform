"""
Resource Mappings Module

Contains mappings between CloudFormation resource types and Terraform resources,
including property mappings and transformation functions.

Supports:
- AWS Provider resources (610+ resource types)
- Databricks Provider resources (60+ resource types)
"""

from cf2tf.resource_mappings.aws_mappings import (
    RESOURCE_TYPE_MAPPING,
    PROPERTY_MAPPINGS,
    get_terraform_resource_type,
    get_property_mapping,
)

from cf2tf.resource_mappings.databricks_mappings import (
    DATABRICKS_RESOURCE_MAPPING,
    DATABRICKS_PROPERTY_MAPPING,
    DATABRICKS_RESOURCE_CATEGORIES,
    get_databricks_mapping,
    get_databricks_property_mapping,
    list_databricks_resources,
    is_databricks_resource,
    get_databricks_provider_block,
)

__all__ = [
    # AWS mappings
    "RESOURCE_TYPE_MAPPING",
    "PROPERTY_MAPPINGS",
    "get_terraform_resource_type",
    "get_property_mapping",
    # Databricks mappings
    "DATABRICKS_RESOURCE_MAPPING",
    "DATABRICKS_PROPERTY_MAPPING",
    "DATABRICKS_RESOURCE_CATEGORIES",
    "get_databricks_mapping",
    "get_databricks_property_mapping",
    "list_databricks_resources",
    "is_databricks_resource",
    "get_databricks_provider_block",
]
