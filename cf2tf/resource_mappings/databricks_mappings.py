"""
Databricks CloudFormation to Terraform Resource Mappings

Databricks resources use the databricks/databricks Terraform provider,
which is separate from the AWS provider. These mappings handle Databricks
resources that may be deployed via CloudFormation custom resources.

Provider: databricks/databricks
Documentation: https://registry.terraform.io/providers/databricks/databricks/latest/docs
"""

from typing import Dict, List, Optional

# Terraform provider configuration for Databricks
DATABRICKS_PROVIDER_CONFIG = """
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

# Configure the Databricks Provider
# Option 1: Using AWS authentication (recommended for AWS deployments)
provider "databricks" {
  alias = "workspace"
  host  = var.databricks_workspace_url
  # Uses AWS credentials from environment or instance profile
}

# Option 2: Using Databricks personal access token
# provider "databricks" {
#   alias = "workspace"
#   host  = var.databricks_workspace_url
#   token = var.databricks_token
# }
"""

# CloudFormation Custom Resource -> Terraform Databricks Resource
# Note: Databricks resources in CloudFormation are typically custom resources
# with ServiceToken pointing to a Lambda function that manages Databricks API calls
DATABRICKS_RESOURCE_MAPPING: Dict[str, str] = {
    # Workspace Management
    "Custom::DatabricksWorkspace": "databricks_mws_workspaces",
    "Custom::Databricks::Workspace": "databricks_mws_workspaces",
    "Databricks::Workspace": "databricks_mws_workspaces",

    # Cluster Management
    "Custom::DatabricksCluster": "databricks_cluster",
    "Custom::Databricks::Cluster": "databricks_cluster",
    "Databricks::Cluster": "databricks_cluster",
    "Custom::DatabricksClusterPolicy": "databricks_cluster_policy",
    "Custom::Databricks::ClusterPolicy": "databricks_cluster_policy",
    "Databricks::ClusterPolicy": "databricks_cluster_policy",
    "Custom::DatabricksInstancePool": "databricks_instance_pool",
    "Custom::Databricks::InstancePool": "databricks_instance_pool",
    "Databricks::InstancePool": "databricks_instance_pool",

    # Job Management
    "Custom::DatabricksJob": "databricks_job",
    "Custom::Databricks::Job": "databricks_job",
    "Databricks::Job": "databricks_job",

    # Notebook Management
    "Custom::DatabricksNotebook": "databricks_notebook",
    "Custom::Databricks::Notebook": "databricks_notebook",
    "Databricks::Notebook": "databricks_notebook",
    "Custom::DatabricksDirectory": "databricks_directory",
    "Custom::Databricks::Directory": "databricks_directory",
    "Databricks::Directory": "databricks_directory",
    "Custom::DatabricksRepo": "databricks_repo",
    "Custom::Databricks::Repo": "databricks_repo",
    "Databricks::Repo": "databricks_repo",

    # Secret Management
    "Custom::DatabricksSecretScope": "databricks_secret_scope",
    "Custom::Databricks::SecretScope": "databricks_secret_scope",
    "Databricks::SecretScope": "databricks_secret_scope",
    "Custom::DatabricksSecret": "databricks_secret",
    "Custom::Databricks::Secret": "databricks_secret",
    "Databricks::Secret": "databricks_secret",
    "Custom::DatabricksSecretAcl": "databricks_secret_acl",
    "Custom::Databricks::SecretAcl": "databricks_secret_acl",
    "Databricks::SecretAcl": "databricks_secret_acl",

    # User and Group Management
    "Custom::DatabricksUser": "databricks_user",
    "Custom::Databricks::User": "databricks_user",
    "Databricks::User": "databricks_user",
    "Custom::DatabricksGroup": "databricks_group",
    "Custom::Databricks::Group": "databricks_group",
    "Databricks::Group": "databricks_group",
    "Custom::DatabricksGroupMember": "databricks_group_member",
    "Custom::Databricks::GroupMember": "databricks_group_member",
    "Databricks::GroupMember": "databricks_group_member",
    "Custom::DatabricksServicePrincipal": "databricks_service_principal",
    "Custom::Databricks::ServicePrincipal": "databricks_service_principal",
    "Databricks::ServicePrincipal": "databricks_service_principal",

    # Permissions
    "Custom::DatabricksPermissions": "databricks_permissions",
    "Custom::Databricks::Permissions": "databricks_permissions",
    "Databricks::Permissions": "databricks_permissions",

    # SQL Warehouse (formerly SQL Endpoints)
    "Custom::DatabricksSqlEndpoint": "databricks_sql_endpoint",
    "Custom::Databricks::SqlEndpoint": "databricks_sql_endpoint",
    "Databricks::SqlEndpoint": "databricks_sql_endpoint",
    "Custom::DatabricksSqlWarehouse": "databricks_sql_endpoint",
    "Custom::Databricks::SqlWarehouse": "databricks_sql_endpoint",
    "Databricks::SqlWarehouse": "databricks_sql_endpoint",
    "Custom::DatabricksSqlQuery": "databricks_sql_query",
    "Custom::Databricks::SqlQuery": "databricks_sql_query",
    "Databricks::SqlQuery": "databricks_sql_query",
    "Custom::DatabricksSqlDashboard": "databricks_sql_dashboard",
    "Custom::Databricks::SqlDashboard": "databricks_sql_dashboard",
    "Databricks::SqlDashboard": "databricks_sql_dashboard",
    "Custom::DatabricksSqlAlert": "databricks_sql_alert",
    "Custom::Databricks::SqlAlert": "databricks_sql_alert",
    "Databricks::SqlAlert": "databricks_sql_alert",

    # Unity Catalog
    "Custom::DatabricksCatalog": "databricks_catalog",
    "Custom::Databricks::Catalog": "databricks_catalog",
    "Databricks::Catalog": "databricks_catalog",
    "Custom::DatabricksSchema": "databricks_schema",
    "Custom::Databricks::Schema": "databricks_schema",
    "Databricks::Schema": "databricks_schema",
    "Custom::DatabricksTable": "databricks_sql_table",
    "Custom::Databricks::Table": "databricks_sql_table",
    "Databricks::Table": "databricks_sql_table",
    "Custom::DatabricksVolume": "databricks_volume",
    "Custom::Databricks::Volume": "databricks_volume",
    "Databricks::Volume": "databricks_volume",
    "Custom::DatabricksExternalLocation": "databricks_external_location",
    "Custom::Databricks::ExternalLocation": "databricks_external_location",
    "Databricks::ExternalLocation": "databricks_external_location",
    "Custom::DatabricksStorageCredential": "databricks_storage_credential",
    "Custom::Databricks::StorageCredential": "databricks_storage_credential",
    "Databricks::StorageCredential": "databricks_storage_credential",
    "Custom::DatabricksMetastore": "databricks_metastore",
    "Custom::Databricks::Metastore": "databricks_metastore",
    "Databricks::Metastore": "databricks_metastore",
    "Custom::DatabricksMetastoreAssignment": "databricks_metastore_assignment",
    "Custom::Databricks::MetastoreAssignment": "databricks_metastore_assignment",
    "Databricks::MetastoreAssignment": "databricks_metastore_assignment",
    "Custom::DatabricksGrants": "databricks_grants",
    "Custom::Databricks::Grants": "databricks_grants",
    "Databricks::Grants": "databricks_grants",

    # Delta Live Tables
    "Custom::DatabricksPipeline": "databricks_pipeline",
    "Custom::Databricks::Pipeline": "databricks_pipeline",
    "Databricks::Pipeline": "databricks_pipeline",

    # MLflow
    "Custom::DatabricksMlflowExperiment": "databricks_mlflow_experiment",
    "Custom::Databricks::MlflowExperiment": "databricks_mlflow_experiment",
    "Databricks::MlflowExperiment": "databricks_mlflow_experiment",
    "Custom::DatabricksMlflowModel": "databricks_mlflow_model",
    "Custom::Databricks::MlflowModel": "databricks_mlflow_model",
    "Databricks::MlflowModel": "databricks_mlflow_model",
    "Custom::DatabricksMlflowWebhook": "databricks_mlflow_webhook",
    "Custom::Databricks::MlflowWebhook": "databricks_mlflow_webhook",
    "Databricks::MlflowWebhook": "databricks_mlflow_webhook",
    "Custom::DatabricksModelServing": "databricks_model_serving",
    "Custom::Databricks::ModelServing": "databricks_model_serving",
    "Databricks::ModelServing": "databricks_model_serving",

    # Vector Search
    "Custom::DatabricksVectorSearchEndpoint": "databricks_vector_search_endpoint",
    "Custom::Databricks::VectorSearchEndpoint": "databricks_vector_search_endpoint",
    "Databricks::VectorSearchEndpoint": "databricks_vector_search_endpoint",
    "Custom::DatabricksVectorSearchIndex": "databricks_vector_search_index",
    "Custom::Databricks::VectorSearchIndex": "databricks_vector_search_index",
    "Databricks::VectorSearchIndex": "databricks_vector_search_index",

    # Networking (AWS-specific)
    "Custom::DatabricksMwsVpcEndpoint": "databricks_mws_vpc_endpoint",
    "Custom::Databricks::MwsVpcEndpoint": "databricks_mws_vpc_endpoint",
    "Databricks::MwsVpcEndpoint": "databricks_mws_vpc_endpoint",
    "Custom::DatabricksMwsNetworks": "databricks_mws_networks",
    "Custom::Databricks::MwsNetworks": "databricks_mws_networks",
    "Databricks::MwsNetworks": "databricks_mws_networks",
    "Custom::DatabricksMwsPrivateAccessSettings": "databricks_mws_private_access_settings",
    "Custom::Databricks::MwsPrivateAccessSettings": "databricks_mws_private_access_settings",
    "Databricks::MwsPrivateAccessSettings": "databricks_mws_private_access_settings",

    # Credentials and Storage (AWS-specific)
    "Custom::DatabricksMwsCredentials": "databricks_mws_credentials",
    "Custom::Databricks::MwsCredentials": "databricks_mws_credentials",
    "Databricks::MwsCredentials": "databricks_mws_credentials",
    "Custom::DatabricksMwsStorageConfigurations": "databricks_mws_storage_configurations",
    "Custom::Databricks::MwsStorageConfigurations": "databricks_mws_storage_configurations",
    "Databricks::MwsStorageConfigurations": "databricks_mws_storage_configurations",
    "Custom::DatabricksMwsCustomerManagedKeys": "databricks_mws_customer_managed_keys",
    "Custom::Databricks::MwsCustomerManagedKeys": "databricks_mws_customer_managed_keys",
    "Databricks::MwsCustomerManagedKeys": "databricks_mws_customer_managed_keys",

    # Global Init Scripts
    "Custom::DatabricksGlobalInitScript": "databricks_global_init_script",
    "Custom::Databricks::GlobalInitScript": "databricks_global_init_script",
    "Databricks::GlobalInitScript": "databricks_global_init_script",

    # DBFS
    "Custom::DatabricksDbfsFile": "databricks_dbfs_file",
    "Custom::Databricks::DbfsFile": "databricks_dbfs_file",
    "Databricks::DbfsFile": "databricks_dbfs_file",

    # Mount Points
    "Custom::DatabricksMount": "databricks_mount",
    "Custom::Databricks::Mount": "databricks_mount",
    "Databricks::Mount": "databricks_mount",
    "Custom::DatabricksAwsS3Mount": "databricks_mount",
    "Custom::Databricks::AwsS3Mount": "databricks_mount",
    "Databricks::AwsS3Mount": "databricks_mount",

    # Tokens
    "Custom::DatabricksToken": "databricks_token",
    "Custom::Databricks::Token": "databricks_token",
    "Databricks::Token": "databricks_token",
    "Custom::DatabricksOboToken": "databricks_obo_token",
    "Custom::Databricks::OboToken": "databricks_obo_token",
    "Databricks::OboToken": "databricks_obo_token",

    # IP Access Lists
    "Custom::DatabricksIpAccessList": "databricks_ip_access_list",
    "Custom::Databricks::IpAccessList": "databricks_ip_access_list",
    "Databricks::IpAccessList": "databricks_ip_access_list",
    "Custom::DatabricksWorkspaceConf": "databricks_workspace_conf",
    "Custom::Databricks::WorkspaceConf": "databricks_workspace_conf",
    "Databricks::WorkspaceConf": "databricks_workspace_conf",

    # Git Credentials
    "Custom::DatabricksGitCredential": "databricks_git_credential",
    "Custom::Databricks::GitCredential": "databricks_git_credential",
    "Databricks::GitCredential": "databricks_git_credential",
}

# Property mappings for common Databricks resources
DATABRICKS_PROPERTY_MAPPING: Dict[str, Dict[str, str]] = {
    "databricks_cluster": {
        "ClusterName": "cluster_name",
        "SparkVersion": "spark_version",
        "NodeTypeId": "node_type_id",
        "NumWorkers": "num_workers",
        "AutoterminationMinutes": "autotermination_minutes",
        "AwsAttributes": "aws_attributes",
        "SparkConf": "spark_conf",
        "SparkEnvVars": "spark_env_vars",
        "CustomTags": "custom_tags",
        "InitScripts": "init_scripts",
        "DriverNodeTypeId": "driver_node_type_id",
        "EnableElasticDisk": "enable_elastic_disk",
        "ClusterLogConf": "cluster_log_conf",
        "InstancePoolId": "instance_pool_id",
        "PolicyId": "policy_id",
        "DataSecurityMode": "data_security_mode",
        "SingleUserName": "single_user_name",
    },
    "databricks_job": {
        "Name": "name",
        "Tasks": "task",
        "Schedule": "schedule",
        "MaxConcurrentRuns": "max_concurrent_runs",
        "TimeoutSeconds": "timeout_seconds",
        "EmailNotifications": "email_notifications",
        "WebhookNotifications": "webhook_notifications",
        "NotificationSettings": "notification_settings",
        "Tags": "tags",
        "GitSource": "git_source",
        "RunAs": "run_as",
    },
    "databricks_notebook": {
        "Path": "path",
        "Content": "content_base64",
        "Language": "language",
        "Source": "source",
        "Format": "format",
    },
    "databricks_sql_endpoint": {
        "Name": "name",
        "ClusterSize": "cluster_size",
        "AutoStopMins": "auto_stop_mins",
        "MinNumClusters": "min_num_clusters",
        "MaxNumClusters": "max_num_clusters",
        "SpotInstancePolicy": "spot_instance_policy",
        "EnablePhoton": "enable_photon",
        "EnableServerlessCompute": "enable_serverless_compute",
        "WarehouseType": "warehouse_type",
        "Channel": "channel",
        "Tags": "tags",
    },
    "databricks_mws_workspaces": {
        "WorkspaceName": "workspace_name",
        "AccountId": "account_id",
        "AwsRegion": "aws_region",
        "CredentialsId": "credentials_id",
        "StorageConfigurationId": "storage_configuration_id",
        "NetworkId": "network_id",
        "ManagedServicesCustomerManagedKeyId": "managed_services_customer_managed_key_id",
        "StorageCustomerManagedKeyId": "storage_customer_managed_key_id",
        "PrivateAccessSettingsId": "private_access_settings_id",
        "PricingTier": "pricing_tier",
        "DeploymentName": "deployment_name",
    },
    "databricks_instance_pool": {
        "InstancePoolName": "instance_pool_name",
        "NodeTypeId": "node_type_id",
        "MinIdleInstances": "min_idle_instances",
        "MaxCapacity": "max_capacity",
        "IdleInstanceAutoterminationMinutes": "idle_instance_autotermination_minutes",
        "AwsAttributes": "aws_attributes",
        "PreloadedSparkVersions": "preloaded_spark_versions",
        "CustomTags": "custom_tags",
    },
    "databricks_secret_scope": {
        "Name": "name",
        "InitialManagePrincipal": "initial_manage_principal",
        "BackendType": "backend_type",
        "KeyvaultMetadata": "keyvault_metadata",
    },
    "databricks_catalog": {
        "Name": "name",
        "Comment": "comment",
        "Properties": "properties",
        "Owner": "owner",
        "StorageRoot": "storage_root",
        "ProviderName": "provider_name",
        "ShareName": "share_name",
        "IsolationMode": "isolation_mode",
    },
    "databricks_schema": {
        "Name": "name",
        "CatalogName": "catalog_name",
        "Comment": "comment",
        "Properties": "properties",
        "Owner": "owner",
        "StorageRoot": "storage_root",
    },
    "databricks_pipeline": {
        "Name": "name",
        "Catalog": "catalog",
        "Target": "target",
        "Storage": "storage",
        "Configuration": "configuration",
        "Clusters": "cluster",
        "Libraries": "library",
        "Continuous": "continuous",
        "Development": "development",
        "Photon": "photon",
        "Channel": "channel",
        "Edition": "edition",
        "Filters": "filters",
        "Notifications": "notification",
    },
}


def get_databricks_mapping(cf_type: str) -> Optional[str]:
    """
    Get Terraform resource type for a CloudFormation Databricks resource.

    Args:
        cf_type: CloudFormation resource type (e.g., "Custom::DatabricksCluster")

    Returns:
        Terraform resource type or None if not found.
    """
    return DATABRICKS_RESOURCE_MAPPING.get(cf_type)


def get_databricks_property_mapping(tf_type: str) -> Dict[str, str]:
    """
    Get property mapping for a Terraform Databricks resource.

    Args:
        tf_type: Terraform resource type (e.g., "databricks_cluster")

    Returns:
        Dictionary mapping CloudFormation properties to Terraform arguments.
    """
    return DATABRICKS_PROPERTY_MAPPING.get(tf_type, {})


def list_databricks_resources() -> List[str]:
    """
    List all supported Databricks resource types.

    Returns:
        List of unique Terraform Databricks resource types.
    """
    return sorted(set(DATABRICKS_RESOURCE_MAPPING.values()))


def is_databricks_resource(cf_type: str) -> bool:
    """
    Check if a CloudFormation resource type is a Databricks resource.

    Args:
        cf_type: CloudFormation resource type

    Returns:
        True if it's a Databricks resource, False otherwise.
    """
    return cf_type in DATABRICKS_RESOURCE_MAPPING or cf_type.startswith("Custom::Databricks")


def get_databricks_provider_block() -> str:
    """
    Get the Terraform provider configuration block for Databricks.

    Returns:
        String containing the provider configuration.
    """
    return DATABRICKS_PROVIDER_CONFIG


# Resource categories for documentation
DATABRICKS_RESOURCE_CATEGORIES = {
    "Workspace Management": [
        "databricks_mws_workspaces",
        "databricks_mws_networks",
        "databricks_mws_credentials",
        "databricks_mws_storage_configurations",
        "databricks_mws_customer_managed_keys",
        "databricks_mws_vpc_endpoint",
        "databricks_mws_private_access_settings",
    ],
    "Compute": [
        "databricks_cluster",
        "databricks_cluster_policy",
        "databricks_instance_pool",
        "databricks_job",
        "databricks_pipeline",
    ],
    "SQL": [
        "databricks_sql_endpoint",
        "databricks_sql_query",
        "databricks_sql_dashboard",
        "databricks_sql_alert",
    ],
    "Unity Catalog": [
        "databricks_metastore",
        "databricks_metastore_assignment",
        "databricks_catalog",
        "databricks_schema",
        "databricks_sql_table",
        "databricks_volume",
        "databricks_external_location",
        "databricks_storage_credential",
        "databricks_grants",
    ],
    "Notebooks & Repos": [
        "databricks_notebook",
        "databricks_directory",
        "databricks_repo",
        "databricks_git_credential",
    ],
    "Security": [
        "databricks_secret_scope",
        "databricks_secret",
        "databricks_secret_acl",
        "databricks_token",
        "databricks_obo_token",
        "databricks_ip_access_list",
        "databricks_permissions",
    ],
    "Identity": [
        "databricks_user",
        "databricks_group",
        "databricks_group_member",
        "databricks_service_principal",
    ],
    "MLflow & AI": [
        "databricks_mlflow_experiment",
        "databricks_mlflow_model",
        "databricks_mlflow_webhook",
        "databricks_model_serving",
        "databricks_vector_search_endpoint",
        "databricks_vector_search_index",
    ],
    "Storage": [
        "databricks_dbfs_file",
        "databricks_mount",
        "databricks_global_init_script",
    ],
    "Configuration": [
        "databricks_workspace_conf",
    ],
}
