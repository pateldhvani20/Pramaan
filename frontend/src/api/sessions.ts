import apiClient from './client';
import type { Session } from './types';

export async function createSession(profileId: string): Promise<Session> {
  const response = await apiClient.post<Session>('/verifications', {
    profileId,
    language: 'en',
  });
  return response.data;
}

export async function getSessionStatus(sessionId: string): Promise<Session> {
  const response = await apiClient.get<Session>(`/verifications/${sessionId}`);
  return response.data;
}
