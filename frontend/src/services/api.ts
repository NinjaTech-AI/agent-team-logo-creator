import type { 
  GenerateLogoRequest, 
  GenerateLogoResponse,
  ImprovePromptRequest,
  ImprovePromptResponse 
} from '../types';

const API_BASE = '/api';

export async function generateLogo(request: GenerateLogoRequest): Promise<GenerateLogoResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to generate logo');
  }

  return response.json();
}

export async function improvePrompt(request: ImprovePromptRequest): Promise<ImprovePromptResponse> {
  const response = await fetch(`${API_BASE}/improve-prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to improve prompt');
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  const response = await fetch(`${API_BASE}/health`);
  return response.ok;
}