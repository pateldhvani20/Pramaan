from aws_cdk import (
    Stack,
    aws_apigateway as apigw,
)
from constructs import Construct

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, pipeline_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        profiles = api.root.add_resource("profiles")
        profiles.add_method("GET") # Mock integration

        verifications = api.root.add_resource("verifications")
        verifications.add_method("POST")

        verification_id = verifications.add_resource("{id}")
        verification_id.add_method("GET")

        uploads = verification_id.add_resource("uploads")
        uploads.add_method("POST")

        run = verification_id.add_resource("run")
        run.add_method("POST")
