"""
AWS CloudFormation to Terraform Resource Mappings

Comprehensive mappings between AWS CloudFormation resource types and their
Terraform AWS provider equivalents.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

# CloudFormation Resource Type -> Terraform Resource Type
RESOURCE_TYPE_MAPPING: Dict[str, str] = {
    # EC2
    "AWS::EC2::Instance": "aws_instance",
    "AWS::EC2::SecurityGroup": "aws_security_group",
    "AWS::EC2::SecurityGroupIngress": "aws_security_group_rule",
    "AWS::EC2::SecurityGroupEgress": "aws_security_group_rule",
    "AWS::EC2::VPC": "aws_vpc",
    "AWS::EC2::Subnet": "aws_subnet",
    "AWS::EC2::InternetGateway": "aws_internet_gateway",
    "AWS::EC2::NatGateway": "aws_nat_gateway",
    "AWS::EC2::RouteTable": "aws_route_table",
    "AWS::EC2::Route": "aws_route",
    "AWS::EC2::SubnetRouteTableAssociation": "aws_route_table_association",
    "AWS::EC2::EIP": "aws_eip",
    "AWS::EC2::VPCGatewayAttachment": "aws_internet_gateway_attachment",
    "AWS::EC2::NetworkInterface": "aws_network_interface",
    "AWS::EC2::Volume": "aws_ebs_volume",
    "AWS::EC2::VolumeAttachment": "aws_volume_attachment",
    "AWS::EC2::LaunchTemplate": "aws_launch_template",
    "AWS::EC2::KeyPair": "aws_key_pair",
    "AWS::EC2::FlowLog": "aws_flow_log",
    "AWS::EC2::NetworkAcl": "aws_network_acl",
    "AWS::EC2::NetworkAclEntry": "aws_network_acl_rule",
    "AWS::EC2::VPCEndpoint": "aws_vpc_endpoint",
    "AWS::EC2::VPCPeeringConnection": "aws_vpc_peering_connection",
    "AWS::EC2::TransitGateway": "aws_ec2_transit_gateway",
    "AWS::EC2::TransitGatewayAttachment": "aws_ec2_transit_gateway_vpc_attachment",
    "AWS::EC2::TransitGatewayRouteTable": "aws_ec2_transit_gateway_route_table",
    "AWS::EC2::TransitGatewayRoute": "aws_ec2_transit_gateway_route",
    "AWS::EC2::TransitGatewayRouteTableAssociation": "aws_ec2_transit_gateway_route_table_association",
    "AWS::EC2::TransitGatewayRouteTablePropagation": "aws_ec2_transit_gateway_route_table_propagation",
    "AWS::EC2::TransitGatewayConnect": "aws_ec2_transit_gateway_connect",
    "AWS::EC2::TransitGatewayConnectPeer": "aws_ec2_transit_gateway_connect_peer",
    "AWS::EC2::TransitGatewayMulticastDomain": "aws_ec2_transit_gateway_multicast_domain",
    "AWS::EC2::TransitGatewayMulticastDomainAssociation": "aws_ec2_transit_gateway_multicast_domain_association",
    "AWS::EC2::TransitGatewayMulticastGroupMember": "aws_ec2_transit_gateway_multicast_group_member",
    "AWS::EC2::TransitGatewayMulticastGroupSource": "aws_ec2_transit_gateway_multicast_group_source",
    "AWS::EC2::TransitGatewayPeeringAttachment": "aws_ec2_transit_gateway_peering_attachment",
    "AWS::EC2::TransitGatewayVpcAttachment": "aws_ec2_transit_gateway_vpc_attachment",
    "AWS::EC2::SubnetCidrBlock": "aws_vpc_ipv4_cidr_block_association",
    "AWS::EC2::VPCCidrBlock": "aws_vpc_ipv4_cidr_block_association",
    "AWS::EC2::EgressOnlyInternetGateway": "aws_egress_only_internet_gateway",
    "AWS::EC2::ClientVpnEndpoint": "aws_ec2_client_vpn_endpoint",
    "AWS::EC2::ClientVpnRoute": "aws_ec2_client_vpn_route",
    "AWS::EC2::ClientVpnAuthorizationRule": "aws_ec2_client_vpn_authorization_rule",
    "AWS::EC2::ClientVpnTargetNetworkAssociation": "aws_ec2_client_vpn_network_association",
    "AWS::EC2::CarrierGateway": "aws_ec2_carrier_gateway",
    "AWS::EC2::LocalGatewayRoute": "aws_ec2_local_gateway_route",
    "AWS::EC2::LocalGatewayRouteTableVPCAssociation": "aws_ec2_local_gateway_route_table_vpc_association",
    "AWS::EC2::PrefixList": "aws_ec2_managed_prefix_list",
    "AWS::EC2::PlacementGroup": "aws_placement_group",
    "AWS::EC2::Host": "aws_ec2_host",
    "AWS::EC2::CapacityReservation": "aws_ec2_capacity_reservation",
    "AWS::EC2::CapacityReservationFleet": "aws_ec2_capacity_reservation",
    "AWS::EC2::SpotFleet": "aws_spot_fleet_request",
    "AWS::EC2::EC2Fleet": "aws_ec2_fleet",
    "AWS::EC2::DHCPOptions": "aws_vpc_dhcp_options",
    "AWS::EC2::VPCDHCPOptionsAssociation": "aws_vpc_dhcp_options_association",
    "AWS::EC2::CustomerGateway": "aws_customer_gateway",
    "AWS::EC2::VPNGateway": "aws_vpn_gateway",
    "AWS::EC2::VPNConnection": "aws_vpn_connection",
    "AWS::EC2::VPNConnectionRoute": "aws_vpn_connection_route",
    "AWS::EC2::VPNGatewayRoutePropagation": "aws_vpn_gateway_route_propagation",
    "AWS::EC2::NetworkInterfaceAttachment": "aws_network_interface_attachment",
    "AWS::EC2::NetworkInterfacePermission": "aws_network_interface",
    "AWS::EC2::TrafficMirrorFilter": "aws_ec2_traffic_mirror_filter",
    "AWS::EC2::TrafficMirrorFilterRule": "aws_ec2_traffic_mirror_filter_rule",
    "AWS::EC2::TrafficMirrorSession": "aws_ec2_traffic_mirror_session",
    "AWS::EC2::TrafficMirrorTarget": "aws_ec2_traffic_mirror_target",
    "AWS::EC2::IPAMPool": "aws_vpc_ipam_pool",
    "AWS::EC2::IPAM": "aws_vpc_ipam",
    "AWS::EC2::IPAMScope": "aws_vpc_ipam_scope",
    "AWS::EC2::IPAMAllocation": "aws_vpc_ipam_pool_cidr_allocation",
    "AWS::EC2::IPAMPoolCidr": "aws_vpc_ipam_pool_cidr",
    "AWS::EC2::EnclaveCertificateIamRoleAssociation": "aws_acm_certificate",
    "AWS::EC2::NetworkInsightsPath": "aws_ec2_network_insights_path",
    "AWS::EC2::NetworkInsightsAnalysis": "aws_ec2_network_insights_analysis",
    "AWS::EC2::NetworkInsightsAccessScope": "aws_ec2_network_insights_path",
    "AWS::EC2::InstanceConnectEndpoint": "aws_ec2_instance_connect_endpoint",

    # Auto Scaling
    "AWS::AutoScaling::AutoScalingGroup": "aws_autoscaling_group",
    "AWS::AutoScaling::LaunchConfiguration": "aws_launch_configuration",
    "AWS::AutoScaling::ScalingPolicy": "aws_autoscaling_policy",
    "AWS::AutoScaling::ScheduledAction": "aws_autoscaling_schedule",

    # ELB / ALB / NLB
    "AWS::ElasticLoadBalancing::LoadBalancer": "aws_elb",
    "AWS::ElasticLoadBalancingV2::LoadBalancer": "aws_lb",
    "AWS::ElasticLoadBalancingV2::TargetGroup": "aws_lb_target_group",
    "AWS::ElasticLoadBalancingV2::Listener": "aws_lb_listener",
    "AWS::ElasticLoadBalancingV2::ListenerRule": "aws_lb_listener_rule",

    # S3
    "AWS::S3::Bucket": "aws_s3_bucket",
    "AWS::S3::BucketPolicy": "aws_s3_bucket_policy",

    # IAM
    "AWS::IAM::Role": "aws_iam_role",
    "AWS::IAM::Policy": "aws_iam_policy",
    "AWS::IAM::ManagedPolicy": "aws_iam_policy",
    "AWS::IAM::InstanceProfile": "aws_iam_instance_profile",
    "AWS::IAM::User": "aws_iam_user",
    "AWS::IAM::Group": "aws_iam_group",
    "AWS::IAM::UserToGroupAddition": "aws_iam_user_group_membership",
    "AWS::IAM::AccessKey": "aws_iam_access_key",
    "AWS::IAM::ServiceLinkedRole": "aws_iam_service_linked_role",

    # RDS
    "AWS::RDS::DBInstance": "aws_db_instance",
    "AWS::RDS::DBCluster": "aws_rds_cluster",
    "AWS::RDS::DBSubnetGroup": "aws_db_subnet_group",
    "AWS::RDS::DBParameterGroup": "aws_db_parameter_group",
    "AWS::RDS::DBClusterParameterGroup": "aws_rds_cluster_parameter_group",
    "AWS::RDS::DBSecurityGroup": "aws_db_security_group",
    "AWS::RDS::OptionGroup": "aws_db_option_group",

    # DynamoDB
    "AWS::DynamoDB::Table": "aws_dynamodb_table",
    "AWS::DynamoDB::GlobalTable": "aws_dynamodb_global_table",

    # Lambda
    "AWS::Lambda::Function": "aws_lambda_function",
    "AWS::Lambda::Permission": "aws_lambda_permission",
    "AWS::Lambda::EventSourceMapping": "aws_lambda_event_source_mapping",
    "AWS::Lambda::Alias": "aws_lambda_alias",
    "AWS::Lambda::Version": "aws_lambda_function_version",
    "AWS::Lambda::LayerVersion": "aws_lambda_layer_version",

    # API Gateway
    "AWS::ApiGateway::RestApi": "aws_api_gateway_rest_api",
    "AWS::ApiGateway::Resource": "aws_api_gateway_resource",
    "AWS::ApiGateway::Method": "aws_api_gateway_method",
    "AWS::ApiGateway::Integration": "aws_api_gateway_integration",
    "AWS::ApiGateway::Deployment": "aws_api_gateway_deployment",
    "AWS::ApiGateway::Stage": "aws_api_gateway_stage",
    "AWS::ApiGateway::ApiKey": "aws_api_gateway_api_key",
    "AWS::ApiGateway::UsagePlan": "aws_api_gateway_usage_plan",
    "AWS::ApiGateway::DomainName": "aws_api_gateway_domain_name",
    "AWS::ApiGateway::BasePathMapping": "aws_api_gateway_base_path_mapping",
    "AWS::ApiGatewayV2::Api": "aws_apigatewayv2_api",
    "AWS::ApiGatewayV2::Stage": "aws_apigatewayv2_stage",
    "AWS::ApiGatewayV2::Route": "aws_apigatewayv2_route",
    "AWS::ApiGatewayV2::Integration": "aws_apigatewayv2_integration",

    # SNS
    "AWS::SNS::Topic": "aws_sns_topic",
    "AWS::SNS::Subscription": "aws_sns_topic_subscription",
    "AWS::SNS::TopicPolicy": "aws_sns_topic_policy",

    # SQS
    "AWS::SQS::Queue": "aws_sqs_queue",
    "AWS::SQS::QueuePolicy": "aws_sqs_queue_policy",

    # CloudWatch
    "AWS::CloudWatch::Alarm": "aws_cloudwatch_metric_alarm",
    "AWS::CloudWatch::Dashboard": "aws_cloudwatch_dashboard",
    "AWS::Logs::LogGroup": "aws_cloudwatch_log_group",
    "AWS::Logs::LogStream": "aws_cloudwatch_log_stream",
    "AWS::Logs::MetricFilter": "aws_cloudwatch_log_metric_filter",
    "AWS::Logs::SubscriptionFilter": "aws_cloudwatch_log_subscription_filter",
    "AWS::Events::Rule": "aws_cloudwatch_event_rule",
    "AWS::Events::EventBus": "aws_cloudwatch_event_bus",

    # KMS
    "AWS::KMS::Key": "aws_kms_key",
    "AWS::KMS::Alias": "aws_kms_alias",

    # Secrets Manager
    "AWS::SecretsManager::Secret": "aws_secretsmanager_secret",
    "AWS::SecretsManager::SecretTargetAttachment": "aws_secretsmanager_secret_version",

    # SSM
    "AWS::SSM::Parameter": "aws_ssm_parameter",
    "AWS::SSM::Document": "aws_ssm_document",
    "AWS::SSM::Association": "aws_ssm_association",

    # CloudFront
    "AWS::CloudFront::Distribution": "aws_cloudfront_distribution",
    "AWS::CloudFront::OriginAccessIdentity": "aws_cloudfront_origin_access_identity",
    "AWS::CloudFront::CachePolicy": "aws_cloudfront_cache_policy",
    "AWS::CloudFront::Function": "aws_cloudfront_function",

    # Route53
    "AWS::Route53::HostedZone": "aws_route53_zone",
    "AWS::Route53::RecordSet": "aws_route53_record",
    "AWS::Route53::RecordSetGroup": "aws_route53_record",
    "AWS::Route53::HealthCheck": "aws_route53_health_check",

    # ACM
    "AWS::CertificateManager::Certificate": "aws_acm_certificate",

    # ECS
    "AWS::ECS::Cluster": "aws_ecs_cluster",
    "AWS::ECS::Service": "aws_ecs_service",
    "AWS::ECS::TaskDefinition": "aws_ecs_task_definition",
    "AWS::ECS::CapacityProvider": "aws_ecs_capacity_provider",

    # EKS
    "AWS::EKS::Cluster": "aws_eks_cluster",
    "AWS::EKS::Nodegroup": "aws_eks_node_group",
    "AWS::EKS::FargateProfile": "aws_eks_fargate_profile",
    "AWS::EKS::Addon": "aws_eks_addon",

    # ECR
    "AWS::ECR::Repository": "aws_ecr_repository",
    "AWS::ECR::LifecyclePolicy": "aws_ecr_lifecycle_policy",

    # Cognito
    "AWS::Cognito::UserPool": "aws_cognito_user_pool",
    "AWS::Cognito::UserPoolClient": "aws_cognito_user_pool_client",
    "AWS::Cognito::UserPoolDomain": "aws_cognito_user_pool_domain",
    "AWS::Cognito::IdentityPool": "aws_cognito_identity_pool",

    # Step Functions
    "AWS::StepFunctions::StateMachine": "aws_sfn_state_machine",
    "AWS::StepFunctions::Activity": "aws_sfn_activity",

    # WAFv2
    "AWS::WAFv2::WebACL": "aws_wafv2_web_acl",
    "AWS::WAFv2::IPSet": "aws_wafv2_ip_set",
    "AWS::WAFv2::RuleGroup": "aws_wafv2_rule_group",
    "AWS::WAFv2::WebACLAssociation": "aws_wafv2_web_acl_association",
    "AWS::WAFv2::RegexPatternSet": "aws_wafv2_regex_pattern_set",
    "AWS::WAFv2::LoggingConfiguration": "aws_wafv2_web_acl_logging_configuration",

    # WAF Classic (Regional)
    "AWS::WAFRegional::WebACL": "aws_wafregional_web_acl",
    "AWS::WAFRegional::Rule": "aws_wafregional_rule",
    "AWS::WAFRegional::RuleGroup": "aws_wafregional_rule_group",
    "AWS::WAFRegional::IPSet": "aws_wafregional_ipset",
    "AWS::WAFRegional::ByteMatchSet": "aws_wafregional_byte_match_set",
    "AWS::WAFRegional::GeoMatchSet": "aws_wafregional_geo_match_set",
    "AWS::WAFRegional::RateBasedRule": "aws_wafregional_rate_based_rule",
    "AWS::WAFRegional::RegexMatchSet": "aws_wafregional_regex_match_set",
    "AWS::WAFRegional::RegexPatternSet": "aws_wafregional_regex_pattern_set",
    "AWS::WAFRegional::SizeConstraintSet": "aws_wafregional_size_constraint_set",
    "AWS::WAFRegional::SqlInjectionMatchSet": "aws_wafregional_sql_injection_match_set",
    "AWS::WAFRegional::XssMatchSet": "aws_wafregional_xss_match_set",
    "AWS::WAFRegional::WebACLAssociation": "aws_wafregional_web_acl_association",

    # WAF Classic (Global/CloudFront)
    "AWS::WAF::WebACL": "aws_waf_web_acl",
    "AWS::WAF::Rule": "aws_waf_rule",
    "AWS::WAF::RuleGroup": "aws_waf_rule_group",
    "AWS::WAF::IPSet": "aws_waf_ipset",
    "AWS::WAF::ByteMatchSet": "aws_waf_byte_match_set",
    "AWS::WAF::GeoMatchSet": "aws_waf_geo_match_set",
    "AWS::WAF::RateBasedRule": "aws_waf_rate_based_rule",
    "AWS::WAF::RegexMatchSet": "aws_waf_regex_match_set",
    "AWS::WAF::RegexPatternSet": "aws_waf_regex_pattern_set",
    "AWS::WAF::SizeConstraintSet": "aws_waf_size_constraint_set",
    "AWS::WAF::SqlInjectionMatchSet": "aws_waf_sql_injection_match_set",
    "AWS::WAF::XssMatchSet": "aws_waf_xss_match_set",

    # AWS Shield (DDoS Protection)
    "AWS::Shield::Protection": "aws_shield_protection",
    "AWS::Shield::ProtectionGroup": "aws_shield_protection_group",
    "AWS::Shield::ProactiveEngagement": "aws_shield_proactive_engagement",
    "AWS::Shield::DRTAccess": "aws_shield_drt_access_log_bucket_association",

    # Firewall Manager
    "AWS::FMS::Policy": "aws_fms_policy",
    "AWS::FMS::NotificationChannel": "aws_fms_admin_account",

    # ElastiCache
    "AWS::ElastiCache::CacheCluster": "aws_elasticache_cluster",
    "AWS::ElastiCache::ReplicationGroup": "aws_elasticache_replication_group",
    "AWS::ElastiCache::SubnetGroup": "aws_elasticache_subnet_group",
    "AWS::ElastiCache::ParameterGroup": "aws_elasticache_parameter_group",

    # Kinesis
    "AWS::Kinesis::Stream": "aws_kinesis_stream",
    "AWS::Kinesis::StreamConsumer": "aws_kinesis_stream_consumer",
    "AWS::KinesisFirehose::DeliveryStream": "aws_kinesis_firehose_delivery_stream",
    # Kinesis Data Analytics
    "AWS::KinesisAnalytics::Application": "aws_kinesis_analytics_application",
    "AWS::KinesisAnalytics::ApplicationOutput": "aws_kinesis_analytics_application",
    "AWS::KinesisAnalyticsV2::Application": "aws_kinesisanalyticsv2_application",
    "AWS::KinesisAnalyticsV2::ApplicationCloudWatchLoggingOption": "aws_kinesisanalyticsv2_application",
    "AWS::KinesisAnalyticsV2::ApplicationOutput": "aws_kinesisanalyticsv2_application",
    "AWS::KinesisAnalyticsV2::ApplicationReferenceDataSource": "aws_kinesisanalyticsv2_application",
    # Kinesis Video
    "AWS::KinesisVideo::Stream": "aws_kinesis_video_stream",
    "AWS::KinesisVideo::SignalingChannel": "aws_kinesis_video_stream",

    # Elasticsearch / OpenSearch
    "AWS::Elasticsearch::Domain": "aws_elasticsearch_domain",
    "AWS::OpenSearchService::Domain": "aws_opensearch_domain",
    # OpenSearch Serverless
    "AWS::OpenSearchServerless::Collection": "aws_opensearchserverless_collection",
    "AWS::OpenSearchServerless::SecurityPolicy": "aws_opensearchserverless_security_policy",
    "AWS::OpenSearchServerless::AccessPolicy": "aws_opensearchserverless_access_policy",
    "AWS::OpenSearchServerless::VpcEndpoint": "aws_opensearchserverless_vpc_endpoint",
    "AWS::OpenSearchServerless::SecurityConfig": "aws_opensearchserverless_security_config",
    "AWS::OpenSearchServerless::LifecyclePolicy": "aws_opensearchserverless_lifecycle_policy",
    # OpenSearch Ingestion
    "AWS::OSIS::Pipeline": "aws_osis_pipeline",

    # Glue
    "AWS::Glue::Database": "aws_glue_catalog_database",
    "AWS::Glue::Table": "aws_glue_catalog_table",
    "AWS::Glue::Crawler": "aws_glue_crawler",
    "AWS::Glue::Job": "aws_glue_job",
    "AWS::Glue::Connection": "aws_glue_connection",
    "AWS::Glue::Trigger": "aws_glue_trigger",
    "AWS::Glue::Workflow": "aws_glue_workflow",
    "AWS::Glue::Partition": "aws_glue_partition",
    "AWS::Glue::DevEndpoint": "aws_glue_dev_endpoint",
    "AWS::Glue::MLTransform": "aws_glue_ml_transform",
    "AWS::Glue::Registry": "aws_glue_registry",
    "AWS::Glue::Schema": "aws_glue_schema",
    "AWS::Glue::SchemaVersion": "aws_glue_schema",
    "AWS::Glue::SecurityConfiguration": "aws_glue_security_configuration",
    "AWS::Glue::Classifier": "aws_glue_classifier",
    "AWS::Glue::DataCatalogEncryptionSettings": "aws_glue_data_catalog_encryption_settings",
    "AWS::Glue::ResourcePolicy": "aws_glue_resource_policy",

    # Athena
    "AWS::Athena::WorkGroup": "aws_athena_workgroup",
    "AWS::Athena::NamedQuery": "aws_athena_named_query",
    "AWS::Athena::DataCatalog": "aws_athena_data_catalog",
    "AWS::Athena::PreparedStatement": "aws_athena_prepared_statement",

    # CodeBuild / CodePipeline / CodeDeploy
    "AWS::CodeBuild::Project": "aws_codebuild_project",
    "AWS::CodePipeline::Pipeline": "aws_codepipeline",
    "AWS::CodeDeploy::Application": "aws_codedeploy_app",
    "AWS::CodeDeploy::DeploymentGroup": "aws_codedeploy_deployment_group",

    # CloudFormation (for nested stacks)
    "AWS::CloudFormation::Stack": "module",
    "AWS::CloudFormation::StackSet": "module",

    # EventBridge
    "AWS::Events::Rule": "aws_cloudwatch_event_rule",
    "AWS::Events::EventBus": "aws_cloudwatch_event_bus",
    "AWS::Scheduler::Schedule": "aws_scheduler_schedule",

    # AppSync
    "AWS::AppSync::GraphQLApi": "aws_appsync_graphql_api",
    "AWS::AppSync::DataSource": "aws_appsync_datasource",
    "AWS::AppSync::Resolver": "aws_appsync_resolver",

    # Backup
    "AWS::Backup::BackupPlan": "aws_backup_plan",
    "AWS::Backup::BackupVault": "aws_backup_vault",
    "AWS::Backup::BackupSelection": "aws_backup_selection",

    # Config
    "AWS::Config::ConfigRule": "aws_config_config_rule",
    "AWS::Config::ConfigurationRecorder": "aws_config_configuration_recorder",
    "AWS::Config::DeliveryChannel": "aws_config_delivery_channel",

    # GuardDuty
    "AWS::GuardDuty::Detector": "aws_guardduty_detector",
    "AWS::GuardDuty::IPSet": "aws_guardduty_ipset",
    "AWS::GuardDuty::ThreatIntelSet": "aws_guardduty_threatintelset",

    # Security Hub
    "AWS::SecurityHub::Hub": "aws_securityhub_account",
    "AWS::SecurityHub::StandardsSubscription": "aws_securityhub_standards_subscription",

    # MSK (Managed Streaming for Kafka)
    "AWS::MSK::Cluster": "aws_msk_cluster",
    "AWS::MSK::Configuration": "aws_msk_configuration",
    "AWS::MSK::ServerlessCluster": "aws_msk_serverless_cluster",
    "AWS::MSK::BatchScramSecret": "aws_msk_scram_secret_association",
    "AWS::MSK::VpcConnection": "aws_msk_vpc_connection",
    "AWS::MSK::Replicator": "aws_msk_replicator",

    # SES
    "AWS::SES::ConfigurationSet": "aws_ses_configuration_set",
    "AWS::SES::Template": "aws_ses_template",
    "AWS::SES::ReceiptRule": "aws_ses_receipt_rule",
    "AWS::SES::ReceiptRuleSet": "aws_ses_receipt_rule_set",

    # EFS (Elastic File System)
    "AWS::EFS::FileSystem": "aws_efs_file_system",
    "AWS::EFS::MountTarget": "aws_efs_mount_target",
    "AWS::EFS::AccessPoint": "aws_efs_access_point",

    # FSx
    "AWS::FSx::FileSystem": "aws_fsx_windows_file_system",
    "AWS::FSx::LustreFileSystem": "aws_fsx_lustre_file_system",
    "AWS::FSx::OpenZFSFileSystem": "aws_fsx_openzfs_file_system",
    "AWS::FSx::OntapFileSystem": "aws_fsx_ontap_file_system",

    # DocumentDB
    "AWS::DocDB::DBCluster": "aws_docdb_cluster",
    "AWS::DocDB::DBInstance": "aws_docdb_cluster_instance",
    "AWS::DocDB::DBSubnetGroup": "aws_docdb_subnet_group",
    "AWS::DocDB::DBClusterParameterGroup": "aws_docdb_cluster_parameter_group",

    # Neptune
    "AWS::Neptune::DBCluster": "aws_neptune_cluster",
    "AWS::Neptune::DBInstance": "aws_neptune_cluster_instance",
    "AWS::Neptune::DBSubnetGroup": "aws_neptune_subnet_group",
    "AWS::Neptune::DBClusterParameterGroup": "aws_neptune_cluster_parameter_group",
    "AWS::Neptune::DBParameterGroup": "aws_neptune_parameter_group",

    # Redshift
    "AWS::Redshift::Cluster": "aws_redshift_cluster",
    "AWS::Redshift::ClusterSubnetGroup": "aws_redshift_subnet_group",
    "AWS::Redshift::ClusterParameterGroup": "aws_redshift_parameter_group",
    "AWS::Redshift::ClusterSecurityGroup": "aws_redshift_security_group",
    "AWS::Redshift::ClusterSecurityGroupIngress": "aws_redshift_security_group",
    "AWS::Redshift::EndpointAccess": "aws_redshift_endpoint_access",
    "AWS::Redshift::EndpointAuthorization": "aws_redshift_endpoint_authorization",
    "AWS::Redshift::EventSubscription": "aws_redshift_event_subscription",
    "AWS::Redshift::ScheduledAction": "aws_redshift_scheduled_action",
    "AWS::Redshift::SnapshotCopyGrant": "aws_redshift_snapshot_copy_grant",
    "AWS::Redshift::SnapshotSchedule": "aws_redshift_snapshot_schedule",
    "AWS::Redshift::SnapshotScheduleAssociation": "aws_redshift_snapshot_schedule_association",

    # Redshift Serverless
    "AWS::RedshiftServerless::Namespace": "aws_redshiftserverless_namespace",
    "AWS::RedshiftServerless::Workgroup": "aws_redshiftserverless_workgroup",
    "AWS::RedshiftServerless::Snapshot": "aws_redshiftserverless_snapshot",

    # MemoryDB
    "AWS::MemoryDB::Cluster": "aws_memorydb_cluster",
    "AWS::MemoryDB::SubnetGroup": "aws_memorydb_subnet_group",
    "AWS::MemoryDB::ParameterGroup": "aws_memorydb_parameter_group",
    "AWS::MemoryDB::ACL": "aws_memorydb_acl",
    "AWS::MemoryDB::User": "aws_memorydb_user",

    # CloudTrail
    "AWS::CloudTrail::Trail": "aws_cloudtrail",

    # X-Ray
    "AWS::XRay::SamplingRule": "aws_xray_sampling_rule",
    "AWS::XRay::Group": "aws_xray_group",

    # CodeCommit
    "AWS::CodeCommit::Repository": "aws_codecommit_repository",

    # CodeArtifact
    "AWS::CodeArtifact::Domain": "aws_codeartifact_domain",
    "AWS::CodeArtifact::Repository": "aws_codeartifact_repository",

    # Amplify
    "AWS::Amplify::App": "aws_amplify_app",
    "AWS::Amplify::Branch": "aws_amplify_branch",
    "AWS::Amplify::Domain": "aws_amplify_domain_association",

    # AppConfig
    "AWS::AppConfig::Application": "aws_appconfig_application",
    "AWS::AppConfig::Environment": "aws_appconfig_environment",
    "AWS::AppConfig::ConfigurationProfile": "aws_appconfig_configuration_profile",
    "AWS::AppConfig::DeploymentStrategy": "aws_appconfig_deployment_strategy",
    "AWS::AppConfig::Deployment": "aws_appconfig_deployment",

    # Direct Connect
    "AWS::DirectConnect::Connection": "aws_dx_connection",
    "AWS::DirectConnect::VirtualInterface": "aws_dx_private_virtual_interface",
    "AWS::DirectConnect::Gateway": "aws_dx_gateway",
    "AWS::DirectConnect::GatewayAssociation": "aws_dx_gateway_association",

    # VPN
    "AWS::EC2::VPNConnection": "aws_vpn_connection",
    "AWS::EC2::VPNGateway": "aws_vpn_gateway",
    "AWS::EC2::CustomerGateway": "aws_customer_gateway",
    "AWS::EC2::VPNConnectionRoute": "aws_vpn_connection_route",

    # Network Firewall
    "AWS::NetworkFirewall::Firewall": "aws_networkfirewall_firewall",
    "AWS::NetworkFirewall::FirewallPolicy": "aws_networkfirewall_firewall_policy",
    "AWS::NetworkFirewall::RuleGroup": "aws_networkfirewall_rule_group",

    # SageMaker
    "AWS::SageMaker::NotebookInstance": "aws_sagemaker_notebook_instance",
    "AWS::SageMaker::Model": "aws_sagemaker_model",
    "AWS::SageMaker::Endpoint": "aws_sagemaker_endpoint",
    "AWS::SageMaker::EndpointConfig": "aws_sagemaker_endpoint_configuration",
    "AWS::SageMaker::Domain": "aws_sagemaker_domain",
    "AWS::SageMaker::UserProfile": "aws_sagemaker_user_profile",
    "AWS::SageMaker::FeatureGroup": "aws_sagemaker_feature_group",
    "AWS::SageMaker::Pipeline": "aws_sagemaker_pipeline",

    # EMR
    "AWS::EMR::Cluster": "aws_emr_cluster",
    "AWS::EMR::InstanceGroupConfig": "aws_emr_instance_group",
    "AWS::EMR::InstanceFleetConfig": "aws_emr_instance_fleet",
    "AWS::EMR::SecurityConfiguration": "aws_emr_security_configuration",
    "AWS::EMR::Studio": "aws_emr_studio",
    "AWS::EMR::StudioSessionMapping": "aws_emr_studio_session_mapping",
    "AWS::EMR::Step": "aws_emr_cluster",
    "AWS::EMR::WALWorkspace": "aws_emr_cluster",

    # EMR Serverless
    "AWS::EMRServerless::Application": "aws_emrserverless_application",

    # EMR Containers (EKS)
    "AWS::EMRContainers::VirtualCluster": "aws_emrcontainers_virtual_cluster",

    # MWAA (Managed Workflows for Apache Airflow)
    "AWS::MWAA::Environment": "aws_mwaa_environment",

    # Transfer Family
    "AWS::Transfer::Server": "aws_transfer_server",
    "AWS::Transfer::User": "aws_transfer_user",
    "AWS::Transfer::Workflow": "aws_transfer_workflow",

    # DataSync
    "AWS::DataSync::Agent": "aws_datasync_agent",
    "AWS::DataSync::LocationS3": "aws_datasync_location_s3",
    "AWS::DataSync::LocationEfs": "aws_datasync_location_efs",
    "AWS::DataSync::LocationNfs": "aws_datasync_location_nfs",
    "AWS::DataSync::LocationFsxWindows": "aws_datasync_location_fsx_windows_file_system",
    "AWS::DataSync::Task": "aws_datasync_task",

    # Application Auto Scaling
    "AWS::ApplicationAutoScaling::ScalableTarget": "aws_appautoscaling_target",
    "AWS::ApplicationAutoScaling::ScalingPolicy": "aws_appautoscaling_policy",
    "AWS::ApplicationAutoScaling::ScheduledAction": "aws_appautoscaling_scheduled_action",

    # Service Catalog
    "AWS::ServiceCatalog::Portfolio": "aws_servicecatalog_portfolio",
    "AWS::ServiceCatalog::Product": "aws_servicecatalog_product",
    "AWS::ServiceCatalog::PortfolioProductAssociation": "aws_servicecatalog_product_portfolio_association",
    "AWS::ServiceCatalog::LaunchRoleConstraint": "aws_servicecatalog_constraint",

    # Organizations
    "AWS::Organizations::Organization": "aws_organizations_organization",
    "AWS::Organizations::OrganizationalUnit": "aws_organizations_organizational_unit",
    "AWS::Organizations::Account": "aws_organizations_account",
    "AWS::Organizations::Policy": "aws_organizations_policy",

    # RAM (Resource Access Manager)
    "AWS::RAM::ResourceShare": "aws_ram_resource_share",
    "AWS::RAM::ResourceShareAccepter": "aws_ram_resource_share_accepter",

    # ACM Private CA
    "AWS::ACMPCA::CertificateAuthority": "aws_acmpca_certificate_authority",
    "AWS::ACMPCA::Certificate": "aws_acmpca_certificate",

    # Inspector
    "AWS::Inspector::AssessmentTarget": "aws_inspector_assessment_target",
    "AWS::Inspector::AssessmentTemplate": "aws_inspector_assessment_template",
    "AWS::InspectorV2::Filter": "aws_inspector2_filter",

    # Macie
    "AWS::Macie::Session": "aws_macie2_account",
    "AWS::Macie::CustomDataIdentifier": "aws_macie2_custom_data_identifier",
    "AWS::Macie::FindingsFilter": "aws_macie2_findings_filter",

    # Detective
    "AWS::Detective::Graph": "aws_detective_graph",
    "AWS::Detective::MemberInvitation": "aws_detective_invitation_accepter",

    # Timestream
    "AWS::Timestream::Database": "aws_timestreamwrite_database",
    "AWS::Timestream::Table": "aws_timestreamwrite_table",

    # QuickSight
    "AWS::QuickSight::DataSource": "aws_quicksight_data_source",
    "AWS::QuickSight::DataSet": "aws_quicksight_data_set",
    "AWS::QuickSight::Dashboard": "aws_quicksight_dashboard",
    "AWS::QuickSight::Analysis": "aws_quicksight_analysis",
    "AWS::QuickSight::Template": "aws_quicksight_template",

    # IoT Core
    "AWS::IoT::Thing": "aws_iot_thing",
    "AWS::IoT::ThingType": "aws_iot_thing_type",
    "AWS::IoT::Policy": "aws_iot_policy",
    "AWS::IoT::TopicRule": "aws_iot_topic_rule",
    "AWS::IoT::Certificate": "aws_iot_certificate",

    # Greengrass
    "AWS::Greengrass::Group": "aws_greengrass_group",
    "AWS::Greengrass::CoreDefinition": "aws_greengrass_core_definition",
    "AWS::Greengrass::FunctionDefinition": "aws_greengrass_function_definition",

    # Batch
    "AWS::Batch::ComputeEnvironment": "aws_batch_compute_environment",
    "AWS::Batch::JobQueue": "aws_batch_job_queue",
    "AWS::Batch::JobDefinition": "aws_batch_job_definition",
    "AWS::Batch::SchedulingPolicy": "aws_batch_scheduling_policy",

    # MediaConvert
    "AWS::MediaConvert::Queue": "aws_media_convert_queue",
    "AWS::MediaConvert::JobTemplate": "aws_media_convert_preset",

    # MediaLive
    "AWS::MediaLive::Channel": "aws_medialive_channel",
    "AWS::MediaLive::Input": "aws_medialive_input",
    "AWS::MediaLive::InputSecurityGroup": "aws_medialive_input_security_group",

    # MediaPackage
    "AWS::MediaPackage::Channel": "aws_media_package_channel",

    # MediaStore
    "AWS::MediaStore::Container": "aws_media_store_container",

    # Elemental
    "AWS::IVS::Channel": "aws_ivs_channel",
    "AWS::IVS::RecordingConfiguration": "aws_ivs_recording_configuration",

    # GameLift
    "AWS::GameLift::Fleet": "aws_gamelift_fleet",
    "AWS::GameLift::Build": "aws_gamelift_build",
    "AWS::GameLift::GameSessionQueue": "aws_gamelift_game_session_queue",

    # Lex
    "AWS::Lex::Bot": "aws_lex_bot",
    "AWS::Lex::BotAlias": "aws_lex_bot_alias",
    "AWS::Lex::Intent": "aws_lex_intent",
    "AWS::Lex::SlotType": "aws_lex_slot_type",

    # Connect
    "AWS::Connect::Instance": "aws_connect_instance",
    "AWS::Connect::ContactFlow": "aws_connect_contact_flow",
    "AWS::Connect::HoursOfOperation": "aws_connect_hours_of_operation",

    # Pinpoint
    "AWS::Pinpoint::App": "aws_pinpoint_app",
    "AWS::Pinpoint::Campaign": "aws_pinpoint_campaign",
    "AWS::Pinpoint::Segment": "aws_pinpoint_segment",
    "AWS::Pinpoint::EmailChannel": "aws_pinpoint_email_channel",
    "AWS::Pinpoint::SMSChannel": "aws_pinpoint_sms_channel",

    # AppFlow
    "AWS::AppFlow::Flow": "aws_appflow_flow",
    "AWS::AppFlow::ConnectorProfile": "aws_appflow_connector_profile",

    # Location Service
    "AWS::Location::Map": "aws_location_map",
    "AWS::Location::PlaceIndex": "aws_location_place_index",
    "AWS::Location::RouteCalculator": "aws_location_route_calculator",
    "AWS::Location::Tracker": "aws_location_tracker",
    "AWS::Location::GeofenceCollection": "aws_location_geofence_collection",

    # Evidently
    "AWS::Evidently::Project": "aws_evidently_project",
    "AWS::Evidently::Feature": "aws_evidently_feature",
    "AWS::Evidently::Launch": "aws_evidently_launch",
    "AWS::Evidently::Experiment": "aws_evidently_experiment",

    # RUM
    "AWS::RUM::AppMonitor": "aws_rum_app_monitor",

    # Global Accelerator
    "AWS::GlobalAccelerator::Accelerator": "aws_globalaccelerator_accelerator",
    "AWS::GlobalAccelerator::Listener": "aws_globalaccelerator_listener",
    "AWS::GlobalAccelerator::EndpointGroup": "aws_globalaccelerator_endpoint_group",

    # App Runner
    "AWS::AppRunner::Service": "aws_apprunner_service",
    "AWS::AppRunner::VpcConnector": "aws_apprunner_vpc_connector",
    "AWS::AppRunner::AutoScalingConfiguration": "aws_apprunner_auto_scaling_configuration_version",

    # Lightsail
    "AWS::Lightsail::Instance": "aws_lightsail_instance",
    "AWS::Lightsail::StaticIp": "aws_lightsail_static_ip",
    "AWS::Lightsail::Database": "aws_lightsail_database",
    "AWS::Lightsail::Bucket": "aws_lightsail_bucket",

    # S3 Object Lambda
    "AWS::S3ObjectLambda::AccessPoint": "aws_s3control_object_lambda_access_point",

    # S3 Outposts
    "AWS::S3Outposts::Bucket": "aws_s3outposts_endpoint",

    # Glacier
    "AWS::Glacier::Vault": "aws_glacier_vault",

    # Backup Gateway
    "AWS::BackupGateway::Hypervisor": "aws_backup_gateway_hypervisor",

    # Systems Manager
    "AWS::SSM::MaintenanceWindow": "aws_ssm_maintenance_window",
    "AWS::SSM::MaintenanceWindowTask": "aws_ssm_maintenance_window_task",
    "AWS::SSM::MaintenanceWindowTarget": "aws_ssm_maintenance_window_target",
    "AWS::SSM::PatchBaseline": "aws_ssm_patch_baseline",
    "AWS::SSM::ResourceDataSync": "aws_ssm_resource_data_sync",

    # License Manager
    "AWS::LicenseManager::License": "aws_licensemanager_license_configuration",
    "AWS::LicenseManager::Grant": "aws_licensemanager_grant",

    # Cost Explorer
    "AWS::CE::AnomalyMonitor": "aws_ce_anomaly_monitor",
    "AWS::CE::AnomalySubscription": "aws_ce_anomaly_subscription",
    "AWS::CE::CostCategory": "aws_ce_cost_category",

    # Budgets
    "AWS::Budgets::Budget": "aws_budgets_budget",
    "AWS::Budgets::BudgetsAction": "aws_budgets_budget_action",

    # Health
    "AWS::Health::HealthCheck": "aws_route53_health_check",

    # Compute Optimizer
    "AWS::ComputeOptimizer::EnrollmentStatus": "aws_compute_optimizer_enrollment_status",

    # Outposts
    "AWS::Outposts::Site": "aws_outposts_site",

    # Proton
    "AWS::Proton::EnvironmentTemplate": "aws_proton_environment_template",
    "AWS::Proton::ServiceTemplate": "aws_proton_service_template",

    # Control Tower
    "AWS::ControlTower::EnabledControl": "aws_controltower_control",

    # Resource Groups
    "AWS::ResourceGroups::Group": "aws_resourcegroups_group",

    # Service Quotas
    "AWS::ServiceQuotas::ServiceQuota": "aws_servicequotas_service_quota",

    # Support
    "AWS::Support::Case": "aws_support_case",

    # Well-Architected Tool
    "AWS::WellArchitected::Workload": "aws_wellarchitected_workload",

    # Chatbot
    "AWS::Chatbot::SlackChannelConfiguration": "aws_chatbot_slack_channel_configuration",

    # SSO
    "AWS::SSO::PermissionSet": "aws_ssoadmin_permission_set",
    "AWS::SSO::Assignment": "aws_ssoadmin_account_assignment",
    "AWS::SSO::InstanceAccessControlAttributeConfiguration": "aws_ssoadmin_instance_access_control_attributes",

    # Identity Store
    "AWS::IdentityStore::Group": "aws_identitystore_group",
    "AWS::IdentityStore::GroupMembership": "aws_identitystore_group_membership",

    # Lake Formation
    "AWS::LakeFormation::DataLakeSettings": "aws_lakeformation_data_lake_settings",
    "AWS::LakeFormation::Permissions": "aws_lakeformation_permissions",
    "AWS::LakeFormation::Resource": "aws_lakeformation_resource",
    "AWS::LakeFormation::Tag": "aws_lakeformation_lf_tag",
    "AWS::LakeFormation::TagAssociation": "aws_lakeformation_resource_lf_tags",
    "AWS::LakeFormation::DataCellsFilter": "aws_lakeformation_data_cells_filter",
    "AWS::LakeFormation::PrincipalPermissions": "aws_lakeformation_permissions",

    # Glue DataBrew
    "AWS::DataBrew::Dataset": "aws_databrew_dataset",
    "AWS::DataBrew::Project": "aws_databrew_project",
    "AWS::DataBrew::Recipe": "aws_databrew_recipe",
    "AWS::DataBrew::Job": "aws_databrew_job",

    # Clean Rooms
    "AWS::CleanRooms::Collaboration": "aws_cleanrooms_collaboration",
    "AWS::CleanRooms::ConfiguredTable": "aws_cleanrooms_configured_table",

    # Data Exchange
    "AWS::DataExchange::DataSet": "aws_dataexchange_data_set",
    "AWS::DataExchange::Revision": "aws_dataexchange_revision",

    # Comprehend
    "AWS::Comprehend::DocumentClassifier": "aws_comprehend_document_classifier",
    "AWS::Comprehend::EntityRecognizer": "aws_comprehend_entity_recognizer",

    # Rekognition
    "AWS::Rekognition::Collection": "aws_rekognition_collection",
    "AWS::Rekognition::Project": "aws_rekognition_project",
    "AWS::Rekognition::StreamProcessor": "aws_rekognition_stream_processor",

    # Textract
    "AWS::Textract::DocumentAnalysis": "aws_textract_document_analysis",

    # Transcribe
    "AWS::Transcribe::LanguageModel": "aws_transcribe_language_model",
    "AWS::Transcribe::Vocabulary": "aws_transcribe_vocabulary",
    "AWS::Transcribe::VocabularyFilter": "aws_transcribe_vocabulary_filter",

    # Translate
    "AWS::Translate::TerminologyData": "aws_translate_terminology",

    # Polly
    "AWS::Polly::Lexicon": "aws_polly_lexicon",

    # Personalize
    "AWS::Personalize::Dataset": "aws_personalize_dataset",
    "AWS::Personalize::Schema": "aws_personalize_schema",
    "AWS::Personalize::DatasetGroup": "aws_personalize_dataset_group",
    "AWS::Personalize::Solution": "aws_personalize_solution",

    # Forecast
    "AWS::Forecast::DatasetGroup": "aws_forecast_dataset_group",
    "AWS::Forecast::Dataset": "aws_forecast_dataset",

    # Kendra
    "AWS::Kendra::Index": "aws_kendra_index",
    "AWS::Kendra::DataSource": "aws_kendra_data_source",
    "AWS::Kendra::Faq": "aws_kendra_faq",

    # Fraud Detector
    "AWS::FraudDetector::Detector": "aws_frauddetector_detector",
    "AWS::FraudDetector::Variable": "aws_frauddetector_variable",
    "AWS::FraudDetector::EntityType": "aws_frauddetector_entity_type",
    "AWS::FraudDetector::EventType": "aws_frauddetector_event_type",
    "AWS::FraudDetector::Label": "aws_frauddetector_label",
    "AWS::FraudDetector::Outcome": "aws_frauddetector_outcome",

    # CodeStar
    "AWS::CodeStar::GitHubRepository": "aws_codestarconnections_host",

    # CodeStar Connections
    "AWS::CodeStarConnections::Connection": "aws_codestarconnections_connection",

    # CodeStar Notifications
    "AWS::CodeStarNotifications::NotificationRule": "aws_codestarnotifications_notification_rule",

    # Developer Tools
    "AWS::DevOpsGuru::NotificationChannel": "aws_devopsguru_notification_channel",
    "AWS::DevOpsGuru::ResourceCollection": "aws_devopsguru_resource_collection",

    # Amazon Bedrock (Generative AI)
    "AWS::Bedrock::Agent": "aws_bedrockagent_agent",
    "AWS::Bedrock::AgentAlias": "aws_bedrockagent_agent_alias",
    "AWS::Bedrock::KnowledgeBase": "aws_bedrockagent_knowledge_base",
    "AWS::Bedrock::DataSource": "aws_bedrockagent_data_source",
    "AWS::Bedrock::Guardrail": "aws_bedrock_guardrail",
    "AWS::Bedrock::GuardrailVersion": "aws_bedrock_guardrail_version",
    "AWS::Bedrock::ApplicationInferenceProfile": "aws_bedrock_inference_profile",

    # Data Pipeline
    "AWS::DataPipeline::Pipeline": "aws_datapipeline_pipeline",

    # FinSpace
    "AWS::FinSpace::Environment": "aws_finspace_kx_environment",

    # HealthLake
    "AWS::HealthLake::FHIRDatastore": "aws_healthlake_fhir_datastore",

    # Lookout for Metrics
    "AWS::LookoutMetrics::AnomalyDetector": "aws_lookoutmetrics_anomaly_detector",
    "AWS::LookoutMetrics::Alert": "aws_lookoutmetrics_alert",

    # Lookout for Equipment
    "AWS::LookoutEquipment::InferenceScheduler": "aws_lookoutequipment_inference_scheduler",

    # Lookout for Vision
    "AWS::LookoutVision::Project": "aws_lookoutvision_project",

    # Panorama
    "AWS::Panorama::ApplicationInstance": "aws_panorama_application_instance",
    "AWS::Panorama::Package": "aws_panorama_package",
    "AWS::Panorama::PackageVersion": "aws_panorama_package_version",

    # Clean Rooms (Data Clean Rooms)
    "AWS::CleanRooms::Collaboration": "aws_cleanrooms_collaboration",
    "AWS::CleanRooms::ConfiguredTable": "aws_cleanrooms_configured_table",
    "AWS::CleanRooms::ConfiguredTableAssociation": "aws_cleanrooms_configured_table_association",
    "AWS::CleanRooms::Membership": "aws_cleanrooms_membership",

    # Entity Resolution
    "AWS::EntityResolution::MatchingWorkflow": "aws_entityresolution_matching_workflow",
    "AWS::EntityResolution::SchemaMapping": "aws_entityresolution_schema_mapping",
    "AWS::EntityResolution::IdMappingWorkflow": "aws_entityresolution_id_mapping_workflow",

    # Managed Grafana
    "AWS::Grafana::Workspace": "aws_grafana_workspace",

    # Managed Prometheus (AMP)
    "AWS::APS::Workspace": "aws_prometheus_workspace",
    "AWS::APS::RuleGroupsNamespace": "aws_prometheus_rule_group_namespace",
    "AWS::APS::AlertManagerDefinition": "aws_prometheus_alert_manager_definition",

    # Q Business (formerly Amazon Q)
    "AWS::QBusiness::Application": "aws_qbusiness_application",
    "AWS::QBusiness::Index": "aws_qbusiness_index",
    "AWS::QBusiness::DataSource": "aws_qbusiness_data_source",
    "AWS::QBusiness::Retriever": "aws_qbusiness_retriever",
    "AWS::QBusiness::WebExperience": "aws_qbusiness_web_experience",

    # CodeWhisperer / Amazon Q Developer
    "AWS::CodeWhisperer::Profile": "aws_codewhisperer_profile",

    # Security Lake
    "AWS::SecurityLake::DataLake": "aws_securitylake_data_lake",
    "AWS::SecurityLake::Subscriber": "aws_securitylake_subscriber",
    "AWS::SecurityLake::AwsLogSource": "aws_securitylake_aws_log_source",
    "AWS::SecurityLake::CustomLogSource": "aws_securitylake_custom_log_source",

    # VPC Lattice
    "AWS::VpcLattice::Service": "aws_vpclattice_service",
    "AWS::VpcLattice::ServiceNetwork": "aws_vpclattice_service_network",
    "AWS::VpcLattice::ServiceNetworkServiceAssociation": "aws_vpclattice_service_network_service_association",
    "AWS::VpcLattice::ServiceNetworkVpcAssociation": "aws_vpclattice_service_network_vpc_association",
    "AWS::VpcLattice::TargetGroup": "aws_vpclattice_target_group",
    "AWS::VpcLattice::Listener": "aws_vpclattice_listener",
    "AWS::VpcLattice::Rule": "aws_vpclattice_listener_rule",
    "AWS::VpcLattice::AccessLogSubscription": "aws_vpclattice_access_log_subscription",
    "AWS::VpcLattice::AuthPolicy": "aws_vpclattice_auth_policy",
    "AWS::VpcLattice::ResourcePolicy": "aws_vpclattice_resource_policy",

    # Verified Access
    "AWS::EC2::VerifiedAccessInstance": "aws_verifiedaccess_instance",
    "AWS::EC2::VerifiedAccessGroup": "aws_verifiedaccess_group",
    "AWS::EC2::VerifiedAccessEndpoint": "aws_verifiedaccess_endpoint",
    "AWS::EC2::VerifiedAccessTrustProvider": "aws_verifiedaccess_trust_provider",

    # Private CA (ACM PCA)
    "AWS::ACMPCA::Certificate": "aws_acmpca_certificate",
    "AWS::ACMPCA::CertificateAuthority": "aws_acmpca_certificate_authority",
    "AWS::ACMPCA::CertificateAuthorityActivation": "aws_acmpca_certificate_authority_certificate",
    "AWS::ACMPCA::Permission": "aws_acmpca_permission",
    "AWS::ACMPCA::Policy": "aws_acmpca_policy",

    # IoT TwinMaker
    "AWS::IoTTwinMaker::Workspace": "aws_iottwinmaker_workspace",
    "AWS::IoTTwinMaker::Entity": "aws_iottwinmaker_entity",
    "AWS::IoTTwinMaker::ComponentType": "aws_iottwinmaker_component_type",
    "AWS::IoTTwinMaker::Scene": "aws_iottwinmaker_scene",
    "AWS::IoTTwinMaker::SyncJob": "aws_iottwinmaker_sync_job",

    # IoT FleetWise
    "AWS::IoTFleetWise::Campaign": "aws_iotfleetwise_campaign",
    "AWS::IoTFleetWise::DecoderManifest": "aws_iotfleetwise_decoder_manifest",
    "AWS::IoTFleetWise::Fleet": "aws_iotfleetwise_fleet",
    "AWS::IoTFleetWise::ModelManifest": "aws_iotfleetwise_model_manifest",
    "AWS::IoTFleetWise::SignalCatalog": "aws_iotfleetwise_signal_catalog",
    "AWS::IoTFleetWise::Vehicle": "aws_iotfleetwise_vehicle",

    # PrivateLink / VPC Endpoints (additional)
    "AWS::EC2::VPCEndpointService": "aws_vpc_endpoint_service",
    "AWS::EC2::VPCEndpointServicePermissions": "aws_vpc_endpoint_service_allowed_principal",
    "AWS::EC2::VPCEndpointConnectionNotification": "aws_vpc_endpoint_connection_notification",

    # Resource Explorer
    "AWS::ResourceExplorer2::Index": "aws_resourceexplorer2_index",
    "AWS::ResourceExplorer2::View": "aws_resourceexplorer2_view",
    "AWS::ResourceExplorer2::DefaultViewAssociation": "aws_resourceexplorer2_view",

    # Omics
    "AWS::Omics::AnnotationStore": "aws_omics_annotation_store",
    "AWS::Omics::ReferenceStore": "aws_omics_reference_store",
    "AWS::Omics::RunGroup": "aws_omics_run_group",
    "AWS::Omics::SequenceStore": "aws_omics_sequence_store",
    "AWS::Omics::VariantStore": "aws_omics_variant_store",
    "AWS::Omics::Workflow": "aws_omics_workflow",

    # SimSpace Weaver
    "AWS::SimSpaceWeaver::Simulation": "aws_simspaceweaver_simulation",

    # Supply Chain
    "AWS::SupplyChain::Instance": "aws_supplychain_instance",

    # Deadline Cloud
    "AWS::Deadline::Farm": "aws_deadline_farm",
    "AWS::Deadline::Queue": "aws_deadline_queue",
    "AWS::Deadline::Fleet": "aws_deadline_fleet",
}

# Property Mappings: CFN Property -> Terraform Attribute
# Format: {cfn_resource_type: {cfn_property: terraform_attribute}}
PROPERTY_MAPPINGS: Dict[str, Dict[str, str]] = {
    "AWS::EC2::Instance": {
        "ImageId": "ami",
        "InstanceType": "instance_type",
        "KeyName": "key_name",
        "SecurityGroupIds": "vpc_security_group_ids",
        "SecurityGroups": "security_groups",
        "SubnetId": "subnet_id",
        "IamInstanceProfile": "iam_instance_profile",
        "UserData": "user_data_base64",
        "AvailabilityZone": "availability_zone",
        "DisableApiTermination": "disable_api_termination",
        "EbsOptimized": "ebs_optimized",
        "Monitoring": "monitoring",
        "PrivateIpAddress": "private_ip",
        "Tenancy": "tenancy",
        "Tags": "tags",
        "BlockDeviceMappings": "root_block_device",
    },
    "AWS::EC2::SecurityGroup": {
        "GroupDescription": "description",
        "GroupName": "name",
        "VpcId": "vpc_id",
        "SecurityGroupIngress": "ingress",
        "SecurityGroupEgress": "egress",
        "Tags": "tags",
    },
    "AWS::EC2::VPC": {
        "CidrBlock": "cidr_block",
        "EnableDnsHostnames": "enable_dns_hostnames",
        "EnableDnsSupport": "enable_dns_support",
        "InstanceTenancy": "instance_tenancy",
        "Tags": "tags",
    },
    "AWS::EC2::Subnet": {
        "VpcId": "vpc_id",
        "CidrBlock": "cidr_block",
        "AvailabilityZone": "availability_zone",
        "MapPublicIpOnLaunch": "map_public_ip_on_launch",
        "Tags": "tags",
    },
    "AWS::EC2::InternetGateway": {
        "Tags": "tags",
    },
    "AWS::EC2::NatGateway": {
        "AllocationId": "allocation_id",
        "SubnetId": "subnet_id",
        "Tags": "tags",
    },
    "AWS::EC2::RouteTable": {
        "VpcId": "vpc_id",
        "Tags": "tags",
    },
    "AWS::EC2::Route": {
        "RouteTableId": "route_table_id",
        "DestinationCidrBlock": "destination_cidr_block",
        "GatewayId": "gateway_id",
        "NatGatewayId": "nat_gateway_id",
        "InstanceId": "instance_id",
        "VpcPeeringConnectionId": "vpc_peering_connection_id",
    },
    "AWS::S3::Bucket": {
        "BucketName": "bucket",
        "AccessControl": "acl",
        "VersioningConfiguration": "versioning",
        "LoggingConfiguration": "logging",
        "WebsiteConfiguration": "website",
        "CorsConfiguration": "cors_rule",
        "LifecycleConfiguration": "lifecycle_rule",
        "ReplicationConfiguration": "replication_configuration",
        "BucketEncryption": "server_side_encryption_configuration",
        "PublicAccessBlockConfiguration": "block_public_acls",
        "Tags": "tags",
    },
    "AWS::IAM::Role": {
        "RoleName": "name",
        "AssumeRolePolicyDocument": "assume_role_policy",
        "Description": "description",
        "MaxSessionDuration": "max_session_duration",
        "Path": "path",
        "PermissionsBoundary": "permissions_boundary",
        "Policies": "inline_policy",
        "ManagedPolicyArns": "managed_policy_arns",
        "Tags": "tags",
    },
    "AWS::IAM::Policy": {
        "PolicyName": "name",
        "PolicyDocument": "policy",
        "Description": "description",
        "Path": "path",
        "Roles": "roles",
        "Users": "users",
        "Groups": "groups",
    },
    "AWS::RDS::DBInstance": {
        "DBInstanceIdentifier": "identifier",
        "DBInstanceClass": "instance_class",
        "Engine": "engine",
        "EngineVersion": "engine_version",
        "MasterUsername": "username",
        "MasterUserPassword": "password",
        "AllocatedStorage": "allocated_storage",
        "StorageType": "storage_type",
        "DBName": "db_name",
        "Port": "port",
        "VPCSecurityGroups": "vpc_security_group_ids",
        "DBSubnetGroupName": "db_subnet_group_name",
        "DBParameterGroupName": "parameter_group_name",
        "AvailabilityZone": "availability_zone",
        "MultiAZ": "multi_az",
        "PubliclyAccessible": "publicly_accessible",
        "StorageEncrypted": "storage_encrypted",
        "KmsKeyId": "kms_key_id",
        "BackupRetentionPeriod": "backup_retention_period",
        "PreferredBackupWindow": "backup_window",
        "PreferredMaintenanceWindow": "maintenance_window",
        "DeletionProtection": "deletion_protection",
        "AutoMinorVersionUpgrade": "auto_minor_version_upgrade",
        "EnablePerformanceInsights": "performance_insights_enabled",
        "MonitoringInterval": "monitoring_interval",
        "Tags": "tags",
    },
    "AWS::Lambda::Function": {
        "FunctionName": "function_name",
        "Runtime": "runtime",
        "Handler": "handler",
        "Code": "filename",
        "Role": "role",
        "Description": "description",
        "MemorySize": "memory_size",
        "Timeout": "timeout",
        "Environment": "environment",
        "VpcConfig": "vpc_config",
        "ReservedConcurrentExecutions": "reserved_concurrent_executions",
        "Layers": "layers",
        "TracingConfig": "tracing_config",
        "Tags": "tags",
    },
    "AWS::DynamoDB::Table": {
        "TableName": "name",
        "AttributeDefinitions": "attribute",
        "KeySchema": "hash_key",
        "BillingMode": "billing_mode",
        "ProvisionedThroughput": "read_capacity",
        "GlobalSecondaryIndexes": "global_secondary_index",
        "LocalSecondaryIndexes": "local_secondary_index",
        "StreamSpecification": "stream_enabled",
        "SSESpecification": "server_side_encryption",
        "PointInTimeRecoverySpecification": "point_in_time_recovery",
        "TimeToLiveSpecification": "ttl",
        "Tags": "tags",
    },
    "AWS::SNS::Topic": {
        "TopicName": "name",
        "DisplayName": "display_name",
        "KmsMasterKeyId": "kms_master_key_id",
        "FifoTopic": "fifo_topic",
        "ContentBasedDeduplication": "content_based_deduplication",
        "Tags": "tags",
    },
    "AWS::SQS::Queue": {
        "QueueName": "name",
        "DelaySeconds": "delay_seconds",
        "MaximumMessageSize": "max_message_size",
        "MessageRetentionPeriod": "message_retention_seconds",
        "ReceiveMessageWaitTimeSeconds": "receive_wait_time_seconds",
        "VisibilityTimeout": "visibility_timeout_seconds",
        "FifoQueue": "fifo_queue",
        "ContentBasedDeduplication": "content_based_deduplication",
        "KmsMasterKeyId": "kms_master_key_id",
        "KmsDataKeyReusePeriodSeconds": "kms_data_key_reuse_period_seconds",
        "RedrivePolicy": "redrive_policy",
        "Tags": "tags",
    },
    "AWS::CloudWatch::Alarm": {
        "AlarmName": "alarm_name",
        "AlarmDescription": "alarm_description",
        "ComparisonOperator": "comparison_operator",
        "EvaluationPeriods": "evaluation_periods",
        "MetricName": "metric_name",
        "Namespace": "namespace",
        "Period": "period",
        "Statistic": "statistic",
        "Threshold": "threshold",
        "ActionsEnabled": "actions_enabled",
        "AlarmActions": "alarm_actions",
        "OKActions": "ok_actions",
        "InsufficientDataActions": "insufficient_data_actions",
        "Dimensions": "dimensions",
        "TreatMissingData": "treat_missing_data",
        "DatapointsToAlarm": "datapoints_to_alarm",
    },
    "AWS::ECS::Cluster": {
        "ClusterName": "name",
        "ClusterSettings": "setting",
        "CapacityProviders": "capacity_providers",
        "Tags": "tags",
    },
    "AWS::ECS::Service": {
        "ServiceName": "name",
        "Cluster": "cluster",
        "TaskDefinition": "task_definition",
        "DesiredCount": "desired_count",
        "LaunchType": "launch_type",
        "NetworkConfiguration": "network_configuration",
        "LoadBalancers": "load_balancer",
        "HealthCheckGracePeriodSeconds": "health_check_grace_period_seconds",
        "DeploymentConfiguration": "deployment_maximum_percent",
        "EnableExecuteCommand": "enable_execute_command",
        "Tags": "tags",
    },
    "AWS::ElasticLoadBalancingV2::LoadBalancer": {
        "Name": "name",
        "Scheme": "internal",
        "Type": "load_balancer_type",
        "Subnets": "subnets",
        "SecurityGroups": "security_groups",
        "IpAddressType": "ip_address_type",
        "LoadBalancerAttributes": "access_logs",
        "Tags": "tags",
    },
    "AWS::KMS::Key": {
        "Description": "description",
        "Enabled": "is_enabled",
        "EnableKeyRotation": "enable_key_rotation",
        "KeyPolicy": "policy",
        "KeySpec": "key_spec",
        "KeyUsage": "key_usage",
        "MultiRegion": "multi_region",
        "PendingWindowInDays": "deletion_window_in_days",
        "Tags": "tags",
    },
    "AWS::Logs::LogGroup": {
        "LogGroupName": "name",
        "RetentionInDays": "retention_in_days",
        "KmsKeyId": "kms_key_id",
        "Tags": "tags",
    },
}


def get_terraform_resource_type(cfn_type: str) -> Optional[str]:
    """
    Get the Terraform resource type for a CloudFormation resource type.

    Args:
        cfn_type: CloudFormation resource type (e.g., "AWS::EC2::Instance")

    Returns:
        Terraform resource type (e.g., "aws_instance") or None if not mapped
    """
    return RESOURCE_TYPE_MAPPING.get(cfn_type)


def get_property_mapping(cfn_type: str, cfn_property: str) -> Optional[str]:
    """
    Get the Terraform attribute name for a CloudFormation property.

    Args:
        cfn_type: CloudFormation resource type
        cfn_property: CloudFormation property name

    Returns:
        Terraform attribute name or None if not mapped
    """
    type_mappings = PROPERTY_MAPPINGS.get(cfn_type, {})
    return type_mappings.get(cfn_property)


def get_all_property_mappings(cfn_type: str) -> Dict[str, str]:
    """
    Get all property mappings for a CloudFormation resource type.

    Args:
        cfn_type: CloudFormation resource type

    Returns:
        Dictionary of CFN property -> Terraform attribute mappings
    """
    return PROPERTY_MAPPINGS.get(cfn_type, {})


# Special transformation functions for complex property conversions
def transform_tags(tags: list) -> Dict[str, str]:
    """Transform CloudFormation Tags format to Terraform tags format."""
    if not tags:
        return {}
    return {tag["Key"]: tag["Value"] for tag in tags if "Key" in tag and "Value" in tag}


def transform_security_group_rules(rules: list, rule_type: str) -> list:
    """Transform CloudFormation security group rules to Terraform format."""
    terraform_rules = []
    for rule in rules or []:
        tf_rule = {
            "from_port": rule.get("FromPort", 0),
            "to_port": rule.get("ToPort", 0),
            "protocol": rule.get("IpProtocol", "-1"),
        }

        if "CidrIp" in rule:
            tf_rule["cidr_blocks"] = [rule["CidrIp"]]
        elif "CidrIpv6" in rule:
            tf_rule["ipv6_cidr_blocks"] = [rule["CidrIpv6"]]
        elif "SourceSecurityGroupId" in rule:
            tf_rule["security_groups"] = [rule["SourceSecurityGroupId"]]

        if "Description" in rule:
            tf_rule["description"] = rule["Description"]

        terraform_rules.append(tf_rule)

    return terraform_rules


def transform_block_device_mappings(mappings: list) -> Dict[str, Any]:
    """Transform CloudFormation BlockDeviceMappings to Terraform format."""
    result = {}

    for mapping in mappings or []:
        device_name = mapping.get("DeviceName", "/dev/sda1")
        ebs = mapping.get("Ebs", {})

        if device_name in ["/dev/sda1", "/dev/xvda"]:
            result["root_block_device"] = {
                "volume_size": ebs.get("VolumeSize"),
                "volume_type": ebs.get("VolumeType", "gp2"),
                "encrypted": ebs.get("Encrypted", False),
                "delete_on_termination": ebs.get("DeleteOnTermination", True),
                "iops": ebs.get("Iops"),
                "throughput": ebs.get("Throughput"),
            }
        else:
            if "ebs_block_device" not in result:
                result["ebs_block_device"] = []
            result["ebs_block_device"].append({
                "device_name": device_name,
                "volume_size": ebs.get("VolumeSize"),
                "volume_type": ebs.get("VolumeType", "gp2"),
                "encrypted": ebs.get("Encrypted", False),
                "delete_on_termination": ebs.get("DeleteOnTermination", True),
                "iops": ebs.get("Iops"),
                "throughput": ebs.get("Throughput"),
            })

    return result


# Pseudo-parameter mappings
PSEUDO_PARAMETER_MAPPING = {
    "AWS::AccountId": "data.aws_caller_identity.current.account_id",
    "AWS::Region": "data.aws_region.current.name",
    "AWS::StackName": "var.stack_name",
    "AWS::StackId": "var.stack_id",
    "AWS::URLSuffix": "data.aws_partition.current.dns_suffix",
    "AWS::Partition": "data.aws_partition.current.partition",
    "AWS::NoValue": "null",
}


# Resource attribute mappings for Ref and GetAtt
RESOURCE_REF_MAPPING = {
    "AWS::EC2::Instance": "id",
    "AWS::EC2::SecurityGroup": "id",
    "AWS::EC2::VPC": "id",
    "AWS::EC2::Subnet": "id",
    "AWS::EC2::InternetGateway": "id",
    "AWS::EC2::NatGateway": "id",
    "AWS::EC2::EIP": "id",
    "AWS::EC2::RouteTable": "id",
    "AWS::S3::Bucket": "id",
    "AWS::IAM::Role": "arn",
    "AWS::IAM::Policy": "arn",
    "AWS::IAM::InstanceProfile": "arn",
    "AWS::Lambda::Function": "arn",
    "AWS::SNS::Topic": "arn",
    "AWS::SQS::Queue": "url",
    "AWS::DynamoDB::Table": "name",
    "AWS::RDS::DBInstance": "id",
    "AWS::KMS::Key": "key_id",
    "AWS::Logs::LogGroup": "name",
}


RESOURCE_GETATT_MAPPING = {
    "AWS::EC2::Instance": {
        "AvailabilityZone": "availability_zone",
        "PrivateDnsName": "private_dns",
        "PrivateIp": "private_ip",
        "PublicDnsName": "public_dns",
        "PublicIp": "public_ip",
    },
    "AWS::EC2::VPC": {
        "CidrBlock": "cidr_block",
        "DefaultNetworkAcl": "default_network_acl_id",
        "DefaultSecurityGroup": "default_security_group_id",
    },
    "AWS::EC2::Subnet": {
        "AvailabilityZone": "availability_zone",
        "CidrBlock": "cidr_block",
        "VpcId": "vpc_id",
    },
    "AWS::EC2::SecurityGroup": {
        "GroupId": "id",
        "VpcId": "vpc_id",
    },
    "AWS::EC2::EIP": {
        "AllocationId": "allocation_id",
        "PublicIp": "public_ip",
    },
    "AWS::S3::Bucket": {
        "Arn": "arn",
        "DomainName": "bucket_domain_name",
        "RegionalDomainName": "bucket_regional_domain_name",
        "WebsiteURL": "website_endpoint",
    },
    "AWS::IAM::Role": {
        "Arn": "arn",
        "RoleId": "unique_id",
    },
    "AWS::Lambda::Function": {
        "Arn": "arn",
    },
    "AWS::SNS::Topic": {
        "TopicName": "name",
        "TopicArn": "arn",
    },
    "AWS::SQS::Queue": {
        "Arn": "arn",
        "QueueName": "name",
        "QueueUrl": "url",
    },
    "AWS::DynamoDB::Table": {
        "Arn": "arn",
        "StreamArn": "stream_arn",
    },
    "AWS::RDS::DBInstance": {
        "Endpoint.Address": "address",
        "Endpoint.Port": "port",
    },
    "AWS::ElasticLoadBalancingV2::LoadBalancer": {
        "DNSName": "dns_name",
        "LoadBalancerArn": "arn",
        "LoadBalancerFullName": "arn_suffix",
    },
}
