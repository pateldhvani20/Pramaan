from aws_cdk import (
    Stack,
    Duration,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
)
from constructs import Construct

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, pipeline_stack, core_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Thin Lambda functions for API endpoints ---

        # Upload controller: generates presigned POST URLs
        upload_lambda = _lambda.Function(self, "UploadControllerLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="workflow.handlers.upload_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(10),
            environment={
                "DOCVERIFY_TABLE": core_stack.table.table_name,
                "RAW_BUCKET": core_stack.raw_bucket.bucket_name,
                "KMS_KEY_ARN": core_stack.kms_key.key_arn,
            }
        )
        core_stack.raw_bucket.grant_put(upload_lambda)
        core_stack.kms_key.grant_encrypt_decrypt(upload_lambda)
        core_stack.table.grant_read_write_data(upload_lambda)

        # Session creator: creates new verification sessions
        session_lambda = _lambda.Function(self, "SessionLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="workflow.handlers.create_session_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(10),
            environment={
                "DOCVERIFY_TABLE": core_stack.table.table_name,
            }
        )
        core_stack.table.grant_read_write_data(session_lambda)
        core_stack.kms_key.grant_encrypt_decrypt(session_lambda)

        # Status getter: returns verification result
        status_lambda = _lambda.Function(self, "StatusLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="workflow.handlers.get_status_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(10),
            environment={
                "DOCVERIFY_TABLE": core_stack.table.table_name,
            }
        )
        core_stack.table.grant_read_data(status_lambda)
        core_stack.kms_key.grant_decrypt(status_lambda)

        # Profiles: returns available verification profiles
        profiles_lambda = _lambda.Function(self, "ProfilesLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="workflow.handlers.list_profiles_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(10),
        )

        # Run: triggers the Step Functions state machine
        run_lambda = _lambda.Function(self, "RunLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="workflow.handlers.run_verification_handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(10),
            environment={
                "DOCVERIFY_TABLE": core_stack.table.table_name,
                "STATE_MACHINE_ARN": pipeline_stack.state_machine.state_machine_arn,
            }
        )
        core_stack.table.grant_read_write_data(run_lambda)
        core_stack.kms_key.grant_encrypt_decrypt(run_lambda)
        pipeline_stack.state_machine.grant_start_execution(run_lambda)

        # --- API Gateway ---

        api = apigw.RestApi(self, "DocVerifyApi",
            rest_api_name="DocVerify Service",
            deploy_options=apigw.StageOptions(
                throttling_rate_limit=20,
                throttling_burst_limit=40
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )

        # GET /profiles → list available verification profiles
        profiles = api.root.add_resource("profiles")
        profiles.add_method("GET", apigw.LambdaIntegration(profiles_lambda))

        # POST /verifications → create new session
        verifications = api.root.add_resource("verifications")
        verifications.add_method("POST", apigw.LambdaIntegration(session_lambda))

        # GET /verifications/{id} → get session status/result
        verification_id = verifications.add_resource("{id}")
        verification_id.add_method("GET", apigw.LambdaIntegration(status_lambda))

        # POST /verifications/{id}/uploads → get presigned upload URL
        uploads = verification_id.add_resource("uploads")
        uploads.add_method("POST", apigw.LambdaIntegration(upload_lambda))

        # POST /verifications/{id}/run → trigger verification pipeline
        run = verification_id.add_resource("run")
        run.add_method("POST", apigw.LambdaIntegration(run_lambda))
