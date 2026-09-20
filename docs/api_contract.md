# DocVerify — API Contract Specification

> **Base URL**: `https://{api-id}.execute-api.ap-south-1.amazonaws.com/prod`  
> **Protocol**: REST over HTTPS (TLS 1.3)  
> **Rate Limit**: 20 requests/second with burst capacity of 40 requests

---

## Endpoints

### 1. `GET /profiles`
List available verification profiles and required document definitions.

**Response `200 OK`**:
```json
[
  {
    "profileId": "post-matric-scholarship-v1",
    "displayName": "Post-Matric Scholarship",
    "rulesetVersion": "2026.09.1",
    "requiredDocCount": 4
  }
]
```

---

### 2. `POST /verifications`
Create a new verification session.

**Request Body**:
```json
{
  "profileId": "post-matric-scholarship-v1",
  "language": "en"
}
```

**Response `201 Created`**:
```json
{
  "sessionId": "a8f1b2c3d4e5f6g7h8i9",
  "profileId": "post-matric-scholarship-v1",
  "rulesetVersion": "2026.09.1",
  "status": "AMBER",
  "createdAt": "2026-09-20T14:30:00Z"
}
```

---

### 3. `POST /verifications/{sessionId}/uploads`
Obtain presigned upload credentials for an intended document.

**Request Body**:
```json
{
  "documentType": "aadhaar",
  "contentType": "application/pdf"
}
```

**Response `200 OK`**:
```json
{
  "documentId": "doc_9f8e7d6c",
  "uploadUrl": "https://docverify-raw.s3.ap-south-1.amazonaws.com/",
  "fields": {
    "key": "uploads/a8f1b2c3d4e5f6g7h8i9/doc_9f8e7d6c.pdf",
    "Content-Type": "application/pdf",
    "x-amz-server-side-encryption": "aws:kms",
    "x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-south-1:...:key/...",
    "policy": "eyJleHBpcmF0aW9uIj...",
    "x-amz-signature": "..."
  }
}
```

---

### 4. `POST /verifications/{sessionId}/run`
Trigger the verification pipeline execution (starts the Step Functions state machine).

**Response `202 Accepted`**:
```json
{
  "sessionId": "a8f1b2c3d4e5f6g7h8i9",
  "executionArn": "arn:aws:states:ap-south-1:...:execution:DocVerifyPipeline:...",
  "status": "RUNNING"
}
```

---

### 5. `GET /verifications/{sessionId}`
Poll verification results and readiness status.

**Response `200 OK`**:
```json
{
  "sessionId": "a8f1b2c3d4e5f6g7h8i9",
  "verificationVersion": 1,
  "readinessStatus": "RED",
  "blockingCount": 1,
  "warningCount": 0,
  "reviewCount": 0,
  "rulesetVersion": "2026.09.1",
  "findings": [
    {
      "findingId": "F-NM-481A",
      "ruleId": "NM-06",
      "category": "identity",
      "severity": "BLOCKING",
      "deterministicMessage": "Name mismatch between aadhaar and marksheet: 'Rahul Borse' vs 'Kunal Borse'. Tokens failed Jaro-Winkler thresholds",
      "deterministicMessageHi": "aadhaar और marksheet में नाम मेल नहीं खाता: 'Rahul Borse' बनाम 'Kunal Borse'।",
      "explanation": "The applicant name differs between your Aadhaar card and your Marksheet. Both documents must belong to the same applicant.",
      "actionSteps": [
        "Upload a marksheet bearing the name Rahul Borse, or update your Aadhaar card to match.",
        "Ensure no initials or family members' certificates are mixed up."
      ],
      "evidence": [
        {"documentType": "aadhaar", "fieldName": "applicantName", "value": "Rahul Borse", "confidence": 98.5},
        {"documentType": "marksheet", "fieldName": "applicantName", "value": "Kunal Borse", "confidence": 97.2}
      ]
    }
  ],
  "documents": [
    {"documentId": "doc_1", "detectedType": "aadhaar", "lifecycle": "DELETED"},
    {"documentId": "doc_2", "detectedType": "marksheet", "lifecycle": "DELETED"}
  ]
}
```
