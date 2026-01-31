import type { LogoRequest, LogoResponse, Style } from './types';

const API_BASE = '/api';

export async function generateLogo(request: LogoRequest): Promise<LogoResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Failed to generate logo (${response.status})`);
  }

  return response.json();
}

export async function getStyles(): Promise<Style[]> {
  const response = await fetch(`${API_BASE}/styles`);
  if (!response.ok) {
    throw new Error('Failed to fetch styles');
  }
  const data = await response.json();
  return data.styles;
}

export async function downloadLogo(
  imageBase64: string,
  size: 256 | 512 | 1024,
  transparent: boolean
): Promise<Blob> {
  const response = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_base64: imageBase64,
      size,
      transparent,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to download logo');
  }

  return response.blob();
}
