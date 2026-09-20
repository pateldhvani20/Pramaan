# DocVerify
A serverless document consistency and expiry verification system for Indian government applications.

## Architecture
```text
[ Client ] -> [ API Gateway ] -> [ Lambda: Workflow ]
                                  -> [ Lambda: Ingestion & Verification (Pure Python) ]
                                  -> [ S3 / DynamoDB ]
```

## Quick Start
```bash
# Install requirements
pip install -r requirements.txt

# Run tests
pytest

# Deploy infrastructure
cdk deploy
```

## Tech Stack
- Python 3.12+ (Pydantic v2)
- AWS CDK (Infrastructure)
- Pytest (Testing)
