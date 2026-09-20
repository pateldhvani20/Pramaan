import apiClient from './client';
import type { UploadCredentials } from './types';

export async function getUploadCredentials(
  sessionId: string,
  filename: string,
  contentType: string
): Promise<UploadCredentials> {
  const response = await apiClient.post<UploadCredentials>(
    `/verifications/${sessionId}/uploads`,
    { filename, contentType }
  );
  return response.data;
}

export async function uploadFileToS3(
  credentials: UploadCredentials,
  file: File
): Promise<void> {
  const formData = new FormData();

  // Append all presigned fields first
  Object.entries(credentials.fields).forEach(([key, value]) => {
    formData.append(key, value);
  });

  // File must be last
  formData.append('file', file);

  // Direct upload to S3 — no auth header
  await fetch(credentials.uploadUrl, {
    method: 'POST',
    body: formData,
  }).then((res) => {
    if (!res.ok && res.status !== 204) {
      throw new Error(`S3 upload failed with status ${res.status}`);
    }
  });
}
