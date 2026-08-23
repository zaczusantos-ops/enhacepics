export interface PresetData {
  id: string;
  name: string;
  description: string;
  icon?: string;
  exposure_compensation: number;
  temperature_kelvin: number;
  tint: number;
  contrast: number;
  highlights_recovery: number;
  shadows_lift: number;
  saturation: number;
  vibrance?: number;
  chromatic_aberration_fix?: number;
  vignette_correction?: number;
  led_clipping_restoration?: number;
  selective_denoise?: number;
  skin_tone_protection_strength: number;
  f_stop_simulation?: number;
  subject_microcontrast?: number;
}

export interface ColorimetryParameters {
  // Vertente 1: Cor, Iluminação & Estilo
  exposure_compensation: number;
  temperature_kelvin: number;
  tint: number;
  contrast: number;
  highlights_recovery: number;
  shadows_lift: number;
  saturation: number;
  vibrance: number;

  // Vertente 2: Correção de Falhas, Anomalias de Lente & Luz Extrema
  chromatic_aberration_fix: number;
  vignette_correction: number;
  lens_distortion_correction: number;
  led_clipping_restoration: number;
  stage_led_tint_suppression: number;
  blue_led_attenuation: number;
  red_magenta_attenuation: number;
  selective_denoise: number;
  skin_tone_protection_strength: number;

  // Vertente 3: Foco Óptico Profissional & Profundidade de Campo (Bokeh)
  focal_point_x: number;
  focal_point_y: number;
  f_stop_simulation: number;
  bokeh_smoothness: number;
  subject_microcontrast: number;

  // Diagnóstico & Presets Contextuais
  scene_moment: string;
  detected_lighting_condition: string;
  detected_scene_type: string;
  subject_description?: string;
  analysis_summary: string;
  suggested_preset: string;
  alternative_presets?: PresetData[];
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
  icon?: string;
  params: ColorimetryParameters;
}
