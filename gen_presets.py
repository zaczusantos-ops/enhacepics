import re

html = open('index.html', encoding='utf-8').read()

new_presets = '''const DEFAULT_TEAM_PRESETS = [
  {
    id: "warm_worship",
    name: "Warm Worship",
    category: "Louvor",
    icon: "fa-sun text-amber-400",
    description: "Ideal para momentos de louvor com iluminação quente de palco.",
    params: {
      exposure_compensation: 0.05,
      temperature_kelvin: 6000,
      tint: 1.0,
      contrast: 1.05,
      highlights: -0.40,
      shadows: 0.30,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.05,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "clean_bright",
    name: "Clean & Bright",
    category: "Culto Matutino",
    icon: "fa-sun text-blue-400",
    description: "Perfeito para cultos durante o dia, com bastante luz natural.",
    params: {
      exposure_compensation: 0.40,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.10,
      highlights: -0.10,
      shadows: 0.10,
      whites: 0.0,
      blacks: 0.15,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "moody_stage",
    name: "Moody Stage",
    category: "Palco",
    icon: "fa-film text-purple-400",
    description: "Destaque para feixes de luz, fumaça de palco e momentos intensos.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.25,
      highlights: -0.60,
      shadows: -0.15,
      whites: 0.0,
      blacks: -0.10,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: -0.15,
      vignette: -0.15
    }
  },
  {
    id: "natural_skin_tone",
    name: "Natural Skin Tone",
    category: "Retratos",
    icon: "fa-user text-emerald-400",
    description: "Foco na fidelidade das cores para fotos de pregadores.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.05,
      highlights: -0.10,
      shadows: 0.05,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.0,
      vignette: -0.05
    }
  },
  {
    id: "deep_matte",
    name: "Deep Matte",
    category: "Editorial",
    icon: "fa-image text-slate-400",
    description: "Visual moderno editorial com pretos elevados.",
    params: {
      exposure_compensation: 0.05,
      temperature_kelvin: 5600,
      tint: 0.0,
      contrast: 0.90,
      highlights: -0.10,
      shadows: 0.15,
      whites: 0.0,
      blacks: 0.30,
      saturation: 0.85,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: -0.10
    }
  },
  {
    id: "golden_hour_glow",
    name: "Golden Hour Glow",
    category: "Externas",
    icon: "fa-sun text-orange-400",
    description: "Para batismos e eventos ao ar livre ao entardecer.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 6200,
      tint: 1.0,
      contrast: 1.05,
      highlights: -0.30,
      shadows: 0.15,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.05,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: -0.05
    }
  },
  {
    id: "stage_light_fix",
    name: "Stage Light Fix",
    category: "Correção",
    icon: "fa-wrench text-red-400",
    description: "Corrige rostos estourados por LEDs vermelhos e azuis do palco.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5200,
      tint: -2.0,
      contrast: 1.0,
      highlights: -0.50,
      shadows: 0.10,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.75,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "monochrome_worship",
    name: "Monochrome Worship",
    category: "P&B",
    icon: "fa-circle-half-stroke text-slate-300",
    description: "P&B solene, foco na emoção e expressões.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.35,
      highlights: -0.20,
      shadows: -0.10,
      whites: 0.0,
      blacks: -0.15,
      saturation: 0.0,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.0,
      vignette: -0.15
    }
  },
  {
    id: "vintage_film",
    name: "Vintage Film",
    category: "Estilo",
    icon: "fa-camera-retro text-amber-600",
    description: "Curva em S suave, ideal para memórias e bastidores.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5800,
      tint: 0.5,
      contrast: 1.15,
      highlights: -0.10,
      shadows: 0.10,
      whites: 0.0,
      blacks: 0.25,
      saturation: 0.90,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: -0.10
    }
  },
  {
    id: "low_light_noise_control",
    name: "Low-Light / Noise Control",
    category: "Correção",
    icon: "fa-moon text-indigo-400",
    description: "Para ambientes muito escuros, ameniza ruído e levanta sombras.",
    params: {
      exposure_compensation: 0.15,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.20,
      shadows: 0.40,
      whites: 0.0,
      blacks: -0.10,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: -0.10,
      dehaze: 0.0,
      vignette: 0.0
    }
  }
];'''

html = re.sub(r'const DEFAULT_TEAM_PRESETS = \[.*?\];', new_presets, html, flags=re.DOTALL)

new_heuristic = '''    function analyzeImageHeuristic(imgElement) {
      if (!imgElement || !imgElement.width) return activeTeam.presets[0].params;

      const cvs = document.createElement('canvas');
      cvs.width = 16;
      cvs.height = 16;
      const ctx = cvs.getContext('2d');
      ctx.drawImage(imgElement, 0, 0, 16, 16);
      const data = ctx.getImageData(0, 0, 16, 16).data;

      let totalBrightness = 0;
      let totalR = 0, totalG = 0, totalB = 0;

      for(let i = 0; i < data.length; i += 4) {
        let r = data[i], g = data[i+1], b = data[i+2];
        totalR += r; totalG += g; totalB += b;
        totalBrightness += (r * 0.299 + g * 0.587 + b * 0.114);
      }

      const pixelCount = 256;
      const avgBrightness = totalBrightness / pixelCount;
      const avgR = totalR / pixelCount;
      const avgB = totalB / pixelCount;

      let chosenId = 'natural_skin_tone';

      if (avgR > avgB + 80 || avgB > avgR + 80) {
        chosenId = 'stage_light_fix';
      } else if (avgBrightness < 60) {
        chosenId = 'low_light_noise_control';
      } else if (avgBrightness > 160) {
        chosenId = 'clean_bright';
      } else if (avgR > avgB + 40 && avgBrightness > 100) {
        chosenId = 'golden_hour_glow';
      } else if (avgBrightness < 100 && avgR > avgB + 20) {
        chosenId = 'warm_worship';
      } else if (avgBrightness < 90) {
        chosenId = 'moody_stage';
      }

      const p = (activeTeam.presets || []).find(x => x.id === chosenId);
      
      const suggestedParams = p ? { ...p.params } : (activeTeam.presets[0] ? activeTeam.presets[0].params : {});
      return { ...suggestedParams, _ai_suggested_id: chosenId };
    }'''

html = re.sub(r'    function analyzeImageHeuristic\(imgElement\) \{[\s\S]*?\n    \}', new_heuristic, html)
open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
