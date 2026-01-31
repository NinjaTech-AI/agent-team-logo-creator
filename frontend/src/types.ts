export type StylePreset = 'minimal' | 'modern' | 'playful' | 'professional' | 'vintage';

export interface Style {
  id: StylePreset;
  name: string;
  description: string;
}

export interface LogoRequest {
  description: string;
  style?: StylePreset;
}

export interface LogoResponse {
  image_base64: string;
  style_applied: string | null;
  generation_time_ms: number;
  prompt_used: string;
}

export interface DownloadRequest {
  image_base64: string;
  size: 256 | 512 | 1024;
  transparent: boolean;
}

export type BackgroundMode = 'light' | 'dark' | 'transparent';
