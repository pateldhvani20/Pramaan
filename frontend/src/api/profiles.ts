import apiClient from './client';
import type { Profile } from './types';

export async function listProfiles(): Promise<Profile[]> {
  const response = await apiClient.get<{ profiles: Profile[] }>('/profiles');
  return response.data.profiles;
}
