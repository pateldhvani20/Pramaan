import aws_cdk as cdk
from stacks.core_stack import CoreStack
from stacks.pipeline_stack import PipelineStack
from stacks.api_stack import ApiStack

app = cdk.App()

core_stack = CoreStack(app, "DocVerifyCoreStack", env=cdk.Environment(region="ap-south-1"))
pipeline_stack = PipelineStack(app, "DocVerifyPipelineStack", core_stack=core_stack, env=cdk.Environment(region="ap-south-1"))
api_stack = ApiStack(app, "DocVerifyApiStack", pipeline_stack=pipeline_stack, env=cdk.Environment(region="ap-south-1"))

app.synth()
