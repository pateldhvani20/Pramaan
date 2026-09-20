import apiClient from './client';
import type { RunResult } from './types';

export async function runVerification(sessionId: string): Promise<RunResult> {
  const response = await apiClient.post<RunResult>(
    `/verifications/${sessionId}/run`
  );
  return response.data;
}
