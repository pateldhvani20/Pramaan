/* ============================================================
   API Type Definitions — matching backend response schemas
   ============================================================ */

export interface Profile {
  profileId: string;
  name: string;
  version: string;
  requiredDocuments: string[];
}

export interface Session {
  sessionId: string;
  profileId: string;
  status: string;
  createdAt: string;
  readinessStatus?: string;
  findings?: Finding[];
  blockingCount?: number;
  warningCount?: number;
  reviewCount?: number;
  verificationVersion?: number;
  documents?: DocumentInfo[];
}

export interface Finding {
  findingId: string;
  ruleId: string;
  category: string;
  severity: 'BLOCKING' | 'WARNING' | 'REVIEW';
  deterministicMessage: string;
  deterministicMessageHi?: string;
  explanation?: string;
  actionSteps?: string[];
  evidence?: Evidence[];
}

export interface Evidence {
  documentType: string;
  fieldName: string;
  value: string;
  confidence: number;
}

export interface DocumentInfo {
  documentId: string;
  detectedType: string;
  lifecycle: string;
}

export interface UploadCredentials {
  uploadUrl: string;
  fields: Record<string, string>;
  key: string;
}

export interface RunResult {
  sessionId: string;
  executionArn: string;
  status: string;
}

export type ReadinessStatus = 'GREEN' | 'AMBER' | 'RED' | 'CREATED' | 'RUNNING' | 'UNKNOWN';
