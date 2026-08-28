import re

html = open('index.html', encoding='utf-8').read()

new_presets = '''const DEFAULT_TEAM_PRESETS = [
  {
    id: "warm_worship",
    name: "Warm Worship (Adoração Acolhedora)",
    category: "Louvor",
    icon: "fa-sun text-amber-400",
    description: "Ideal para momentos de louvor com iluminação quente de palco.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 6100, 
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.40,
      shadows: 0.30,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "clean_bright",
    name: "Clean & Bright (Culto Matutino)",
    category: "Matutino",
    icon: "fa-sun text-blue-400",
    description: "Perfeito para cultos durante o dia, batismos e reuniões com bastante luz natural.",
    params: {
      exposure_compensation: 0.40,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.10,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.15,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "moody_stage",
    name: "Moody Stage (Palco Dramático)",
    category: "Jovens",
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
      clarity: 0.0,
      dehaze: -0.15,
      vignette: 0.0
    }
  },
  {
    id: "natural_skin_tone",
    name: "Natural Skin Tone (Retratos)",
    category: "Retratos",
    icon: "fa-user text-emerald-400",
    description: "Foco na fidelidade das cores para fotos de pregadores.",
    params: {
      exposure_compensation: 0.10, 
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.15, 
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "deep_matte",
    name: "Deep Matte (Editorial)",
    category: "Redes Sociais",
    icon: "fa-image text-slate-400",
    description: "Visual moderno para posts do Instagram e materiais de divulgação.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 0.90,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.20,
      saturation: 0.85,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "golden_hour_glow",
    name: "Golden Hour Glow (Externas)",
    category: "Externas",
    icon: "fa-sun text-orange-400",
    description: "Para batismos em rios, retiros e piqueniques de jovens ao entardecer.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 6500,
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.30,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "stage_light_fix",
    name: "Stage Light Fix (Correção)",
    category: "Correção",
    icon: "fa-wrench text-red-400",
    description: "Corrige rostos estourados por LEDs fortes.",
    params: {
      exposure_compensation: 0.15,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: -0.50,
      shadows: 0.0,
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
    name: "Monochrome Worship (P&B)",
    category: "Fine Art",
    icon: "fa-circle-half-stroke text-slate-300",
    description: "Transmite solenidade, emoção e foco nas expressões.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.35,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.0,
      saturation: 0.0,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "vintage_film",
    name: "Vintage Film (Comunhão)",
    category: "Estilo",
    icon: "fa-camera-retro text-amber-600",
    description: "Curva em S suave com pretos lavados, para memórias e comunhão.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5800,
      tint: 0.0,
      contrast: 1.15,
      highlights: 0.0,
      shadows: 0.0,
      whites: 0.0,
      blacks: 0.20,
      saturation: 0.90,
      vibrance: 1.0,
      clarity: 0.0,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "low_light_noise_control",
    name: "Low-Light Noise Control",
    category: "Noturno",
    icon: "fa-moon text-indigo-400",
    description: "Para fotos tiradas com ISO elevado em momentos mais escuros do culto.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.0,
      highlights: 0.0,
      shadows: 0.40,
      whites: 0.0,
      blacks: -0.10,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: -0.20,
      dehaze: 0.0,
      vignette: 0.0
    }
  }
];'''

html = re.sub(r'const DEFAULT_TEAM_PRESETS = \[.*?\];', new_presets, html, flags=re.DOTALL)

clear_storage = '''    function loadTeamData() {
      // CLEAR CACHE TO FORCE NEW PRESETS
      localStorage.removeItem('CHURCHPHOTO_SAVED_PRESETS_MASTER');
      
      const key = getStorageTeamKey();'''

html = re.sub(r'    function loadTeamData\(\) \{\n.*?(const key = getStorageTeamKey\(\);)', clear_storage, html, flags=re.DOTALL)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
