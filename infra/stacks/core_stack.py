from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_kms as kms,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam
)
from constructs import Construct

class CoreStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.kms_key = kms.Key(self, "DocVerifyKey",
            alias="alias/docverify",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
            pending_window=Duration.days(7)
        )

        self.raw_bucket = s3.Bucket(self, "RawBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(1), abort_incomplete_multipart_upload_after=Duration.days(1))],
            versioned=False,
            enforce_ssl=True,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.POST],
                allowed_origins=["*"], # Should be locked down in prod
                allowed_headers=["*"]
            )],
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        self.raw_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.DENY,
            principals=[iam.AnyPrincipal()],
            actions=["s3:*"],
            resources=[self.raw_bucket.bucket_arn, f"{self.raw_bucket.bucket_arn}/*"],
            conditions={"Bool": {"aws:SecureTransport": "false"}}
        ))

        self.results_bucket = s3.Bucket(self, "ResultsBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(30))],
            versioned=True,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        self.table = dynamodb.Table(self, "StateTable",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.kms_key,
            point_in_time_recovery=True,
            time_to_live_attribute="expiresAt",
            removal_policy=RemovalPolicy.DESTROY
        )
