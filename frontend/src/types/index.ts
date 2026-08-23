export interface ColorimetryParameters {
  exposure_compensation: number;
  temperature_kelvin: number;
  tint: number;
  contrast: number;
  highlights_recovery: number;
  shadows_lift: number;
  saturation: number;
  stage_led_tint_suppression: number;
  blue_led_attenuation: number;
  red_magenta_attenuation: number;
  skin_tone_protection_strength: number;
  denoise_strength: number;
  unsharp_mask_amount: number;
  unsharp_mask_radius: number;
  detected_lighting_condition: string;
  detected_scene_type: string;
  analysis_summary: string;
  suggested_preset: string;
}

export interface ProcessedImageMetadata {
  width: number;
  height: number;
  original_format: string;
  output_format: string;
  execution_time_ms: number;
  parameters_applied: ColorimetryParameters;
  histogram?: {
    r: number[];
    g: number[];
    b: number[];
  };
}

export interface QueueItem {
  id: string;
  file: File;
  previewUrl: string;
  status: 'idle' | 'uploading' | 'analyzing' | 'processing' | 'completed' | 'error';
  errorMessage?: string;
  originalBase64?: string;
  processedBase64?: string;
  metadata?: ProcessedImageMetadata;
  analysis?: ColorimetryParameters;
  currentParams?: ColorimetryParameters;
}

export interface ChurchPreset {
  id: string;
  name: string;
  description: string;
  params: ColorimetryParameters;
}
