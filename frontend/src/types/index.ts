export interface GenerateLogoRequest {
  business_name: string;
  style?: string;
  description?: string;  // #32: Story/description
  size?: string;  // #33: Size selection
  resolution?: string;  // #33: Resolution
  filters?: string[];  // #34: Filters/effects
  transparency?: boolean;  // #36: Transparency
  preview_mode?: boolean;  // #35: Preview mode
}

export interface GenerateLogoResponse {
  success: boolean;
  logo_url: string;
  generation_id: string;
  error?: string;
}

export interface ImprovePromptRequest {
  business_name: string;
  style: string;
  description?: string;
  current_prompt?: string;
}

export interface ImprovePromptResponse {
  success: boolean;
  improved_prompt?: string;
  preview_url?: string;
  error?: string;
}

export type LogoStyle =
  | 'minimalist'
  | 'modern'
  | 'classic'
  | 'playful'
  | 'professional'
  | 'vintage';

export type LogoSize = '1024x1024' | '1792x1024' | '1024x1792';

export type LogoResolution = 'standard' | 'high' | 'hd';

export type LogoFilter =
  | 'vibrant'
  | 'muted'
  | 'monochrome'
  | 'gradient'
  | 'neon'
  | 'pastel'
  | 'bold'
  | 'soft';