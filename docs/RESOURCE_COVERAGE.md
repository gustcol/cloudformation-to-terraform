# CloudFormation to Terraform Resource Coverage

This document provides comprehensive documentation of all supported AWS CloudFormation resource types and their corresponding Terraform equivalents.

## Overview

| Provider | Resources Mapped | Categories |
|----------|-----------------|------------|
| AWS | 616+ | 167 services |
| Databricks | 50 | 10 categories |
| **Total** | **666+** | |

## AWS Provider Resources

### Compute Services

#### EC2 (78 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::Instance` | `aws_instance` |
| `AWS::EC2::SecurityGroup` | `aws_security_group` |
| `AWS::EC2::SecurityGroupIngress` | `aws_security_group_rule` |
| `AWS::EC2::SecurityGroupEgress` | `aws_security_group_rule` |
| `AWS::EC2::VPC` | `aws_vpc` |
| `AWS::EC2::Subnet` | `aws_subnet` |
| `AWS::EC2::InternetGateway` | `aws_internet_gateway` |
| `AWS::EC2::NatGateway` | `aws_nat_gateway` |
| `AWS::EC2::RouteTable` | `aws_route_table` |
| `AWS::EC2::Route` | `aws_route` |
| `AWS::EC2::SubnetRouteTableAssociation` | `aws_route_table_association` |
| `AWS::EC2::EIP` | `aws_eip` |
| `AWS::EC2::VPCGatewayAttachment` | `aws_internet_gateway_attachment` |
| `AWS::EC2::NetworkInterface` | `aws_network_interface` |
| `AWS::EC2::Volume` | `aws_ebs_volume` |
| `AWS::EC2::VolumeAttachment` | `aws_volume_attachment` |
| `AWS::EC2::LaunchTemplate` | `aws_launch_template` |
| `AWS::EC2::KeyPair` | `aws_key_pair` |
| `AWS::EC2::FlowLog` | `aws_flow_log` |
| `AWS::EC2::NetworkAcl` | `aws_network_acl` |
| `AWS::EC2::NetworkAclEntry` | `aws_network_acl_rule` |
| `AWS::EC2::VPCEndpoint` | `aws_vpc_endpoint` |
| `AWS::EC2::VPCPeeringConnection` | `aws_vpc_peering_connection` |
| `AWS::EC2::PlacementGroup` | `aws_placement_group` |
| `AWS::EC2::Host` | `aws_ec2_host` |
| `AWS::EC2::CapacityReservation` | `aws_ec2_capacity_reservation` |
| `AWS::EC2::SpotFleet` | `aws_spot_fleet_request` |
| `AWS::EC2::EC2Fleet` | `aws_ec2_fleet` |

#### Transit Gateway (14 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::TransitGateway` | `aws_ec2_transit_gateway` |
| `AWS::EC2::TransitGatewayAttachment` | `aws_ec2_transit_gateway_vpc_attachment` |
| `AWS::EC2::TransitGatewayVpcAttachment` | `aws_ec2_transit_gateway_vpc_attachment` |
| `AWS::EC2::TransitGatewayRouteTable` | `aws_ec2_transit_gateway_route_table` |
| `AWS::EC2::TransitGatewayRoute` | `aws_ec2_transit_gateway_route` |
| `AWS::EC2::TransitGatewayRouteTableAssociation` | `aws_ec2_transit_gateway_route_table_association` |
| `AWS::EC2::TransitGatewayRouteTablePropagation` | `aws_ec2_transit_gateway_route_table_propagation` |
| `AWS::EC2::TransitGatewayConnect` | `aws_ec2_transit_gateway_connect` |
| `AWS::EC2::TransitGatewayConnectPeer` | `aws_ec2_transit_gateway_connect_peer` |
| `AWS::EC2::TransitGatewayMulticastDomain` | `aws_ec2_transit_gateway_multicast_domain` |
| `AWS::EC2::TransitGatewayMulticastDomainAssociation` | `aws_ec2_transit_gateway_multicast_domain_association` |
| `AWS::EC2::TransitGatewayMulticastGroupMember` | `aws_ec2_transit_gateway_multicast_group_member` |
| `AWS::EC2::TransitGatewayMulticastGroupSource` | `aws_ec2_transit_gateway_multicast_group_source` |
| `AWS::EC2::TransitGatewayPeeringAttachment` | `aws_ec2_transit_gateway_peering_attachment` |

#### Client VPN (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::ClientVpnEndpoint` | `aws_ec2_client_vpn_endpoint` |
| `AWS::EC2::ClientVpnRoute` | `aws_ec2_client_vpn_route` |
| `AWS::EC2::ClientVpnAuthorizationRule` | `aws_ec2_client_vpn_authorization_rule` |
| `AWS::EC2::ClientVpnTargetNetworkAssociation` | `aws_ec2_client_vpn_network_association` |

#### VPN (5 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::CustomerGateway` | `aws_customer_gateway` |
| `AWS::EC2::VPNGateway` | `aws_vpn_gateway` |
| `AWS::EC2::VPNConnection` | `aws_vpn_connection` |
| `AWS::EC2::VPNConnectionRoute` | `aws_vpn_connection_route` |
| `AWS::EC2::VPNGatewayRoutePropagation` | `aws_vpn_gateway_route_propagation` |

#### IPAM (5 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::IPAM` | `aws_vpc_ipam` |
| `AWS::EC2::IPAMPool` | `aws_vpc_ipam_pool` |
| `AWS::EC2::IPAMScope` | `aws_vpc_ipam_scope` |
| `AWS::EC2::IPAMAllocation` | `aws_vpc_ipam_pool_cidr_allocation` |
| `AWS::EC2::IPAMPoolCidr` | `aws_vpc_ipam_pool_cidr` |

#### Traffic Mirror (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::TrafficMirrorFilter` | `aws_ec2_traffic_mirror_filter` |
| `AWS::EC2::TrafficMirrorFilterRule` | `aws_ec2_traffic_mirror_filter_rule` |
| `AWS::EC2::TrafficMirrorSession` | `aws_ec2_traffic_mirror_session` |
| `AWS::EC2::TrafficMirrorTarget` | `aws_ec2_traffic_mirror_target` |

#### Auto Scaling (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::AutoScaling::AutoScalingGroup` | `aws_autoscaling_group` |
| `AWS::AutoScaling::LaunchConfiguration` | `aws_launch_configuration` |
| `AWS::AutoScaling::ScalingPolicy` | `aws_autoscaling_policy` |
| `AWS::AutoScaling::ScheduledAction` | `aws_autoscaling_schedule` |

#### Lambda (6 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Lambda::Function` | `aws_lambda_function` |
| `AWS::Lambda::Permission` | `aws_lambda_permission` |
| `AWS::Lambda::EventSourceMapping` | `aws_lambda_event_source_mapping` |
| `AWS::Lambda::Alias` | `aws_lambda_alias` |
| `AWS::Lambda::Version` | `aws_lambda_function_version` |
| `AWS::Lambda::LayerVersion` | `aws_lambda_layer_version` |

### Container Services

#### ECS (5 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::ECS::Cluster` | `aws_ecs_cluster` |
| `AWS::ECS::Service` | `aws_ecs_service` |
| `AWS::ECS::TaskDefinition` | `aws_ecs_task_definition` |
| `AWS::ECS::TaskSet` | `aws_ecs_task_set` |
| `AWS::ECS::CapacityProvider` | `aws_ecs_capacity_provider` |

#### EKS (5 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EKS::Cluster` | `aws_eks_cluster` |
| `AWS::EKS::Nodegroup` | `aws_eks_node_group` |
| `AWS::EKS::FargateProfile` | `aws_eks_fargate_profile` |
| `AWS::EKS::Addon` | `aws_eks_addon` |
| `AWS::EKS::IdentityProviderConfig` | `aws_eks_identity_provider_config` |

### Database Services

#### RDS (7 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::RDS::DBInstance` | `aws_db_instance` |
| `AWS::RDS::DBCluster` | `aws_rds_cluster` |
| `AWS::RDS::DBSubnetGroup` | `aws_db_subnet_group` |
| `AWS::RDS::DBParameterGroup` | `aws_db_parameter_group` |
| `AWS::RDS::DBClusterParameterGroup` | `aws_rds_cluster_parameter_group` |
| `AWS::RDS::DBSecurityGroup` | `aws_db_security_group` |
| `AWS::RDS::OptionGroup` | `aws_db_option_group` |

#### DynamoDB (2 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::DynamoDB::Table` | `aws_dynamodb_table` |
| `AWS::DynamoDB::GlobalTable` | `aws_dynamodb_global_table` |

#### Redshift (12 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Redshift::Cluster` | `aws_redshift_cluster` |
| `AWS::Redshift::ClusterParameterGroup` | `aws_redshift_parameter_group` |
| `AWS::Redshift::ClusterSubnetGroup` | `aws_redshift_subnet_group` |
| `AWS::Redshift::ClusterSecurityGroup` | `aws_redshift_security_group` |
| `AWS::Redshift::EndpointAccess` | `aws_redshift_endpoint_access` |
| `AWS::Redshift::EndpointAuthorization` | `aws_redshift_endpoint_authorization` |
| `AWS::Redshift::EventSubscription` | `aws_redshift_event_subscription` |
| `AWS::Redshift::ScheduledAction` | `aws_redshift_scheduled_action` |
| `AWS::Redshift::SnapshotCopyGrant` | `aws_redshift_snapshot_copy_grant` |
| `AWS::Redshift::SnapshotSchedule` | `aws_redshift_snapshot_schedule` |
| `AWS::Redshift::SnapshotScheduleAssociation` | `aws_redshift_snapshot_schedule_association` |
| `AWS::Redshift::ClusterSecurityGroupIngress` | `aws_redshift_security_group` |

#### Redshift Serverless (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::RedshiftServerless::Namespace` | `aws_redshiftserverless_namespace` |
| `AWS::RedshiftServerless::Workgroup` | `aws_redshiftserverless_workgroup` |
| `AWS::RedshiftServerless::Snapshot` | `aws_redshiftserverless_snapshot` |

### Data Analytics Services

#### AWS Glue (17 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Glue::Database` | `aws_glue_catalog_database` |
| `AWS::Glue::Table` | `aws_glue_catalog_table` |
| `AWS::Glue::Crawler` | `aws_glue_crawler` |
| `AWS::Glue::Job` | `aws_glue_job` |
| `AWS::Glue::Connection` | `aws_glue_connection` |
| `AWS::Glue::Trigger` | `aws_glue_trigger` |
| `AWS::Glue::Workflow` | `aws_glue_workflow` |
| `AWS::Glue::Partition` | `aws_glue_partition` |
| `AWS::Glue::DevEndpoint` | `aws_glue_dev_endpoint` |
| `AWS::Glue::MLTransform` | `aws_glue_ml_transform` |
| `AWS::Glue::Registry` | `aws_glue_registry` |
| `AWS::Glue::Schema` | `aws_glue_schema` |
| `AWS::Glue::SchemaVersion` | `aws_glue_schema` |
| `AWS::Glue::SecurityConfiguration` | `aws_glue_security_configuration` |
| `AWS::Glue::Classifier` | `aws_glue_classifier` |
| `AWS::Glue::DataCatalogEncryptionSettings` | `aws_glue_data_catalog_encryption_settings` |
| `AWS::Glue::ResourcePolicy` | `aws_glue_resource_policy` |

#### Lake Formation (7 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::LakeFormation::Resource` | `aws_lakeformation_resource` |
| `AWS::LakeFormation::Permissions` | `aws_lakeformation_permissions` |
| `AWS::LakeFormation::DataLakeSettings` | `aws_lakeformation_data_lake_settings` |
| `AWS::LakeFormation::Tag` | `aws_lakeformation_lf_tag` |
| `AWS::LakeFormation::TagAssociation` | `aws_lakeformation_resource_lf_tags` |
| `AWS::LakeFormation::DataCellsFilter` | `aws_lakeformation_data_cells_filter` |
| `AWS::LakeFormation::PrincipalPermissions` | `aws_lakeformation_permissions` |

#### Athena (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Athena::WorkGroup` | `aws_athena_workgroup` |
| `AWS::Athena::NamedQuery` | `aws_athena_named_query` |
| `AWS::Athena::DataCatalog` | `aws_athena_data_catalog` |
| `AWS::Athena::PreparedStatement` | `aws_athena_prepared_statement` |

#### EMR (8 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EMR::Cluster` | `aws_emr_cluster` |
| `AWS::EMR::InstanceGroupConfig` | `aws_emr_instance_group` |
| `AWS::EMR::InstanceFleetConfig` | `aws_emr_instance_fleet` |
| `AWS::EMR::SecurityConfiguration` | `aws_emr_security_configuration` |
| `AWS::EMR::Studio` | `aws_emr_studio` |
| `AWS::EMR::StudioSessionMapping` | `aws_emr_studio_session_mapping` |
| `AWS::EMR::Step` | `aws_emr_cluster` |
| `AWS::EMR::WALWorkspace` | `aws_emr_cluster` |

#### Kinesis (10 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Kinesis::Stream` | `aws_kinesis_stream` |
| `AWS::Kinesis::StreamConsumer` | `aws_kinesis_stream_consumer` |
| `AWS::KinesisFirehose::DeliveryStream` | `aws_kinesis_firehose_delivery_stream` |
| `AWS::KinesisAnalytics::Application` | `aws_kinesis_analytics_application` |
| `AWS::KinesisAnalytics::ApplicationOutput` | `aws_kinesis_analytics_application` |
| `AWS::KinesisAnalytics::ApplicationReferenceDataSource` | `aws_kinesis_analytics_application` |
| `AWS::KinesisAnalyticsV2::Application` | `aws_kinesisanalyticsv2_application` |
| `AWS::KinesisAnalyticsV2::ApplicationOutput` | `aws_kinesisanalyticsv2_application` |
| `AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource` | `aws_kinesisanalyticsv2_application` |
| `AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption` | `aws_kinesisanalyticsv2_application` |

#### MSK - Managed Streaming for Kafka (6 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::MSK::Cluster` | `aws_msk_cluster` |
| `AWS::MSK::Configuration` | `aws_msk_configuration` |
| `AWS::MSK::ServerlessCluster` | `aws_msk_serverless_cluster` |
| `AWS::MSK::BatchScramSecret` | `aws_msk_scram_secret_association` |
| `AWS::MSK::VpcConnection` | `aws_msk_vpc_connection` |
| `AWS::MSK::Replicator` | `aws_msk_replicator` |

### Search Services

#### OpenSearch (2 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::OpenSearchService::Domain` | `aws_opensearch_domain` |
| `AWS::Elasticsearch::Domain` | `aws_elasticsearch_domain` |

#### OpenSearch Serverless (6 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::OpenSearchServerless::Collection` | `aws_opensearchserverless_collection` |
| `AWS::OpenSearchServerless::SecurityPolicy` | `aws_opensearchserverless_security_policy` |
| `AWS::OpenSearchServerless::AccessPolicy` | `aws_opensearchserverless_access_policy` |
| `AWS::OpenSearchServerless::VpcEndpoint` | `aws_opensearchserverless_vpc_endpoint` |
| `AWS::OpenSearchServerless::SecurityConfig` | `aws_opensearchserverless_security_config` |
| `AWS::OpenSearchServerless::LifecyclePolicy` | `aws_opensearchserverless_lifecycle_policy` |

### AI/ML Services

#### Amazon Bedrock (7 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Bedrock::Agent` | `aws_bedrockagent_agent` |
| `AWS::Bedrock::AgentAlias` | `aws_bedrockagent_agent_alias` |
| `AWS::Bedrock::KnowledgeBase` | `aws_bedrockagent_knowledge_base` |
| `AWS::Bedrock::DataSource` | `aws_bedrockagent_data_source` |
| `AWS::Bedrock::Guardrail` | `aws_bedrock_guardrail` |
| `AWS::Bedrock::GuardrailVersion` | `aws_bedrock_guardrail_version` |
| `AWS::Bedrock::ApplicationInferenceProfile` | `aws_bedrock_inference_profile` |

#### SageMaker (8 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::SageMaker::Model` | `aws_sagemaker_model` |
| `AWS::SageMaker::Endpoint` | `aws_sagemaker_endpoint` |
| `AWS::SageMaker::EndpointConfig` | `aws_sagemaker_endpoint_configuration` |
| `AWS::SageMaker::NotebookInstance` | `aws_sagemaker_notebook_instance` |
| `AWS::SageMaker::Domain` | `aws_sagemaker_domain` |
| `AWS::SageMaker::UserProfile` | `aws_sagemaker_user_profile` |
| `AWS::SageMaker::App` | `aws_sagemaker_app` |
| `AWS::SageMaker::FeatureGroup` | `aws_sagemaker_feature_group` |

### Security Services

#### IAM (9 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::IAM::Role` | `aws_iam_role` |
| `AWS::IAM::Policy` | `aws_iam_policy` |
| `AWS::IAM::ManagedPolicy` | `aws_iam_policy` |
| `AWS::IAM::InstanceProfile` | `aws_iam_instance_profile` |
| `AWS::IAM::User` | `aws_iam_user` |
| `AWS::IAM::Group` | `aws_iam_group` |
| `AWS::IAM::UserToGroupAddition` | `aws_iam_user_group_membership` |
| `AWS::IAM::AccessKey` | `aws_iam_access_key` |
| `AWS::IAM::ServiceLinkedRole` | `aws_iam_service_linked_role` |

#### KMS (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::KMS::Key` | `aws_kms_key` |
| `AWS::KMS::Alias` | `aws_kms_alias` |
| `AWS::KMS::ReplicaKey` | `aws_kms_replica_key` |

#### Secrets Manager (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::SecretsManager::Secret` | `aws_secretsmanager_secret` |
| `AWS::SecretsManager::SecretTargetAttachment` | `aws_secretsmanager_secret_version` |
| `AWS::SecretsManager::ResourcePolicy` | `aws_secretsmanager_secret_policy` |

#### Security Lake (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::SecurityLake::DataLake` | `aws_securitylake_data_lake` |
| `AWS::SecurityLake::Subscriber` | `aws_securitylake_subscriber` |
| `AWS::SecurityLake::SubscriberNotification` | `aws_securitylake_subscriber_notification` |
| `AWS::SecurityLake::AwsLogSource` | `aws_securitylake_aws_log_source` |

#### WAF (37 resources)
- WAFv2 (6 resources)
- WAF Classic (12 resources)
- WAF Regional (13 resources)
- Shield (3 resources)
- FMS (3 resources)

#### VPC Lattice (10 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::VpcLattice::Service` | `aws_vpclattice_service` |
| `AWS::VpcLattice::ServiceNetwork` | `aws_vpclattice_service_network` |
| `AWS::VpcLattice::ServiceNetworkServiceAssociation` | `aws_vpclattice_service_network_service_association` |
| `AWS::VpcLattice::ServiceNetworkVpcAssociation` | `aws_vpclattice_service_network_vpc_association` |
| `AWS::VpcLattice::TargetGroup` | `aws_vpclattice_target_group` |
| `AWS::VpcLattice::Listener` | `aws_vpclattice_listener` |
| `AWS::VpcLattice::Rule` | `aws_vpclattice_listener_rule` |
| `AWS::VpcLattice::AccessLogSubscription` | `aws_vpclattice_access_log_subscription` |
| `AWS::VpcLattice::AuthPolicy` | `aws_vpclattice_auth_policy` |
| `AWS::VpcLattice::ResourcePolicy` | `aws_vpclattice_resource_policy` |

#### Verified Access (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EC2::VerifiedAccessInstance` | `aws_verifiedaccess_instance` |
| `AWS::EC2::VerifiedAccessGroup` | `aws_verifiedaccess_group` |
| `AWS::EC2::VerifiedAccessEndpoint` | `aws_verifiedaccess_endpoint` |
| `AWS::EC2::VerifiedAccessTrustProvider` | `aws_verifiedaccess_trust_provider` |

### Storage Services

#### S3 (2 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::S3::Bucket` | `aws_s3_bucket` |
| `AWS::S3::BucketPolicy` | `aws_s3_bucket_policy` |

#### EFS (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::EFS::FileSystem` | `aws_efs_file_system` |
| `AWS::EFS::MountTarget` | `aws_efs_mount_target` |
| `AWS::EFS::AccessPoint` | `aws_efs_access_point` |

### Messaging Services

#### SQS (2 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::SQS::Queue` | `aws_sqs_queue` |
| `AWS::SQS::QueuePolicy` | `aws_sqs_queue_policy` |

#### SNS (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::SNS::Topic` | `aws_sns_topic` |
| `AWS::SNS::Subscription` | `aws_sns_topic_subscription` |
| `AWS::SNS::TopicPolicy` | `aws_sns_topic_policy` |

#### EventBridge (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::Events::Rule` | `aws_cloudwatch_event_rule` |
| `AWS::Events::EventBus` | `aws_cloudwatch_event_bus` |
| `AWS::Events::EventBusPolicy` | `aws_cloudwatch_event_bus_policy` |
| `AWS::Events::Archive` | `aws_cloudwatch_event_archive` |

### API Services

#### API Gateway (10 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::ApiGateway::RestApi` | `aws_api_gateway_rest_api` |
| `AWS::ApiGateway::Resource` | `aws_api_gateway_resource` |
| `AWS::ApiGateway::Method` | `aws_api_gateway_method` |
| `AWS::ApiGateway::Integration` | `aws_api_gateway_integration` |
| `AWS::ApiGateway::Deployment` | `aws_api_gateway_deployment` |
| `AWS::ApiGateway::Stage` | `aws_api_gateway_stage` |
| `AWS::ApiGateway::ApiKey` | `aws_api_gateway_api_key` |
| `AWS::ApiGateway::UsagePlan` | `aws_api_gateway_usage_plan` |
| `AWS::ApiGateway::DomainName` | `aws_api_gateway_domain_name` |
| `AWS::ApiGateway::BasePathMapping` | `aws_api_gateway_base_path_mapping` |

#### API Gateway V2 (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `AWS::ApiGatewayV2::Api` | `aws_apigatewayv2_api` |
| `AWS::ApiGatewayV2::Stage` | `aws_apigatewayv2_stage` |
| `AWS::ApiGatewayV2::Route` | `aws_apigatewayv2_route` |
| `AWS::ApiGatewayV2::Integration` | `aws_apigatewayv2_integration` |

---

## Databricks Provider Resources

The Databricks provider (databricks/databricks) is used for managing Databricks resources deployed on AWS.

### Provider Configuration

```hcl
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

provider "databricks" {
  host = var.databricks_workspace_url
  # Uses AWS credentials from environment or instance profile
}
```

### Workspace Management (7 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::DatabricksWorkspace` | `databricks_mws_workspaces` |
| `Custom::Databricks::MwsNetworks` | `databricks_mws_networks` |
| `Custom::Databricks::MwsCredentials` | `databricks_mws_credentials` |
| `Custom::Databricks::MwsStorageConfigurations` | `databricks_mws_storage_configurations` |
| `Custom::Databricks::MwsCustomerManagedKeys` | `databricks_mws_customer_managed_keys` |
| `Custom::Databricks::MwsVpcEndpoint` | `databricks_mws_vpc_endpoint` |
| `Custom::Databricks::MwsPrivateAccessSettings` | `databricks_mws_private_access_settings` |

### Compute (5 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::DatabricksCluster` | `databricks_cluster` |
| `Custom::Databricks::ClusterPolicy` | `databricks_cluster_policy` |
| `Custom::Databricks::InstancePool` | `databricks_instance_pool` |
| `Custom::Databricks::Job` | `databricks_job` |
| `Custom::Databricks::Pipeline` | `databricks_pipeline` |

### SQL (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::SqlEndpoint` | `databricks_sql_endpoint` |
| `Custom::Databricks::SqlQuery` | `databricks_sql_query` |
| `Custom::Databricks::SqlDashboard` | `databricks_sql_dashboard` |
| `Custom::Databricks::SqlAlert` | `databricks_sql_alert` |

### Unity Catalog (9 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::Metastore` | `databricks_metastore` |
| `Custom::Databricks::MetastoreAssignment` | `databricks_metastore_assignment` |
| `Custom::Databricks::Catalog` | `databricks_catalog` |
| `Custom::Databricks::Schema` | `databricks_schema` |
| `Custom::Databricks::Table` | `databricks_sql_table` |
| `Custom::Databricks::Volume` | `databricks_volume` |
| `Custom::Databricks::ExternalLocation` | `databricks_external_location` |
| `Custom::Databricks::StorageCredential` | `databricks_storage_credential` |
| `Custom::Databricks::Grants` | `databricks_grants` |

### Notebooks & Repos (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::Notebook` | `databricks_notebook` |
| `Custom::Databricks::Directory` | `databricks_directory` |
| `Custom::Databricks::Repo` | `databricks_repo` |
| `Custom::Databricks::GitCredential` | `databricks_git_credential` |

### Security (7 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::SecretScope` | `databricks_secret_scope` |
| `Custom::Databricks::Secret` | `databricks_secret` |
| `Custom::Databricks::SecretAcl` | `databricks_secret_acl` |
| `Custom::Databricks::Token` | `databricks_token` |
| `Custom::Databricks::OboToken` | `databricks_obo_token` |
| `Custom::Databricks::IpAccessList` | `databricks_ip_access_list` |
| `Custom::Databricks::Permissions` | `databricks_permissions` |

### Identity (4 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::User` | `databricks_user` |
| `Custom::Databricks::Group` | `databricks_group` |
| `Custom::Databricks::GroupMember` | `databricks_group_member` |
| `Custom::Databricks::ServicePrincipal` | `databricks_service_principal` |

### MLflow & AI (6 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::MlflowExperiment` | `databricks_mlflow_experiment` |
| `Custom::Databricks::MlflowModel` | `databricks_mlflow_model` |
| `Custom::Databricks::MlflowWebhook` | `databricks_mlflow_webhook` |
| `Custom::Databricks::ModelServing` | `databricks_model_serving` |
| `Custom::Databricks::VectorSearchEndpoint` | `databricks_vector_search_endpoint` |
| `Custom::Databricks::VectorSearchIndex` | `databricks_vector_search_index` |

### Storage (3 resources)
| CloudFormation Type | Terraform Type |
|---------------------|----------------|
| `Custom::Databricks::DbfsFile` | `databricks_dbfs_file` |
| `Custom::Databricks::Mount` | `databricks_mount` |
| `Custom::Databricks::GlobalInitScript` | `databricks_global_init_script` |

---

## Security Rules

The framework includes 88 security rules based on Checkov patterns covering:

| Category | Rules |
|----------|-------|
| S3 Security | 8 |
| EC2/VPC Security | 12 |
| RDS Security | 6 |
| IAM Security | 8 |
| Lambda Security | 4 |
| API Gateway Security | 4 |
| CloudFront Security | 4 |
| ElasticSearch/OpenSearch | 6 |
| OpenSearch Serverless | 3 |
| Bedrock AI Security | 1 |
| Security Lake | 1 |
| VPC Lattice | 2 |
| Verified Access | 1 |
| Prometheus/APS | 1 |
| Kinesis Analytics | 1 |
| Other Services | 26 |

---

## User Data Templates

The framework includes 18 user data templates for EC2 instance customization:

| Category | Templates |
|----------|-----------|
| Base OS | amazon-linux-2, ubuntu |
| Web Servers | nginx, apache |
| Containers | docker, kubernetes-node |
| Monitoring | cloudwatch-agent, prometheus-node-exporter |
| Databases | mysql, postgresql |
| Security | hardening-base, fail2ban |

---

## Version Information

- **Last Updated**: January 2025
- **AWS Provider Version**: ~> 5.0
- **Databricks Provider Version**: ~> 1.0
- **Total AWS Resources**: 616+
- **Total Databricks Resources**: 50
- **Total Security Rules**: 88
