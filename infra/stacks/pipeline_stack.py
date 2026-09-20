from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets
)
from constructs import Construct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, core_stack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        def create_lambda(name, handler):
            return _lambda.Function(self, name,
                runtime=_lambda.Runtime.PYTHON_3_12,
                handler=handler,
                code=_lambda.Code.from_asset("../backend"),
                timeout=Duration.seconds(30),
                environment={
                    "DOCVERIFY_TABLE": core_stack.table.table_name
                }
            )

        ingest_lambda = create_lambda("IngestGateLambda", "workflow.handlers.ingest_gate_handler")
        extraction_lambda = create_lambda("ExtractionLambda", "workflow.handlers.extraction_handler")
        classification_lambda = create_lambda("ClassificationLambda", "workflow.handlers.classification_handler")
        completeness_lambda = create_lambda("CompletenessLambda", "workflow.handlers.completeness_handler")
        verification_lambda = create_lambda("VerificationLambda", "workflow.handlers.verification_handler")
        explanation_lambda = create_lambda("ExplanationLambda", "workflow.handlers.explanation_handler")
        persist_lambda = create_lambda("PersistLambda", "workflow.handlers.persist_handler")
        cleanup_lambda = create_lambda("CleanupLambda", "workflow.handlers.cleanup_handler")

        for fn in [ingest_lambda, extraction_lambda, classification_lambda, completeness_lambda, verification_lambda, explanation_lambda, persist_lambda, cleanup_lambda]:
            core_stack.table.grant_read_write_data(fn)
            core_stack.kms_key.grant_encrypt_decrypt(fn)

        ingest_task = tasks.LambdaInvoke(self, "IngestGate", lambda_function=ingest_lambda)
        extraction_task = tasks.LambdaInvoke(self, "Extraction", lambda_function=extraction_lambda)
        classification_task = tasks.LambdaInvoke(self, "Classification", lambda_function=classification_lambda)
        completeness_task = tasks.LambdaInvoke(self, "Completeness", lambda_function=completeness_lambda)
        verification_task = tasks.LambdaInvoke(self, "Verification", lambda_function=verification_lambda)
        explanation_task = tasks.LambdaInvoke(self, "Explanation", lambda_function=explanation_lambda)
        persist_task = tasks.LambdaInvoke(self, "Persist", lambda_function=persist_lambda)
        cleanup_task = tasks.LambdaInvoke(self, "Cleanup", lambda_function=cleanup_lambda)

        definition = ingest_task.next(extraction_task).next(classification_task).next(completeness_task).next(verification_task).next(explanation_task).next(persist_task).next(cleanup_task)

        self.state_machine = sfn.StateMachine(self, "DocVerifyStateMachine",
            definition=definition,
            timeout=Duration.minutes(5)
        )

        rule = events.Rule(self, "S3UploadRule",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={"bucket": {"name": [core_stack.raw_bucket.bucket_name]}}
            )
        )
        rule.add_target(targets.SfnStateMachine(self.state_machine))
