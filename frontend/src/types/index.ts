export interface GenerateLogoRequest {
  business_name: string;
  style?: string;
}

export interface GenerateLogoResponse {
  success: boolean;
  logo_url: string;
  generation_id: string;
  error?: string;
}

export type LogoStyle =
  | 'minimalist'
  | 'modern'
  | 'classic'
  | 'playful'
  | 'professional'
  | 'vintage';
