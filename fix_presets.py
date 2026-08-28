import re
html = open('index.html', encoding='utf-8').read()

new_presets = '''const DEFAULT_TEAM_PRESETS = [
  {
    id: "luz_quente_natural",
    name: "Luz Quente Natural",
    category: "Louvor",
    icon: "fa-sun text-amber-400",
    description: "Tons de pele acolhedores e calor orgânico de forma suave.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5600,
      tint: -1.0,
      contrast: 1.03,
      highlights: -0.20,
      shadows: 0.20,
      whites: 0.05,
      blacks: 0.0,
      saturation: 1.02,
      vibrance: 1.0,
      clarity: 0.05,
      dehaze: 0.0,
      vignette: -0.05
    }
  },
  {
    id: "clean_moderno_neutro",
    name: "Clean / Moderno Neutro",
    category: "Pregação",
    icon: "fa-wand-magic text-blue-400",
    description: "Balanço de estúdio limpo e realista, sem exageros.",
    params: {
      exposure_compensation: 0.05,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.05,
      highlights: -0.30,
      shadows: 0.15,
      whites: -0.05,
      blacks: 0.05,
      saturation: 0.98,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: -0.10
    }
  },
  {
    id: "moody_contraste_cenico",
    name: "Moody / Contraste Cênico",
    category: "Jovens",
    icon: "fa-film text-purple-400",
    description: "Visual cinematográfico moderado com sombras mais densas.",
    params: {
      exposure_compensation: -0.05,
      temperature_kelvin: 5200,
      tint: 2.0,
      contrast: 1.12,
      highlights: -0.35,
      shadows: 0.10,
      whites: -0.10,
      blacks: -0.10,
      saturation: 1.02,
      vibrance: 1.0,
      clarity: 0.20,
      dehaze: 0.05,
      vignette: -0.20
    }
  },
  {
    id: "vintage_analogico",
    name: "Vintage Analógico",
    category: "Estilo",
    icon: "fa-camera-retro text-amber-500",
    description: "Pretos levemente esmaecidos e contraste orgânico realista.",
    params: {
      exposure_compensation: 0.0,
      temperature_kelvin: 5700,
      tint: 1.5,
      contrast: 0.98,
      highlights: -0.15,
      shadows: 0.25,
      whites: -0.10,
      blacks: 0.20,
      saturation: 0.90,
      vibrance: 1.0,
      clarity: -0.05,
      dehaze: 0.0,
      vignette: -0.10
    }
  },
  {
    id: "pb_dramatico",
    name: "P&B Dramático",
    category: "Fine Art",
    icon: "fa-circle-half-stroke text-slate-300",
    description: "Preto e branco balanceado, sem perder detalhes nas sombras.",
    params: {
      exposure_compensation: 0.05,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.15,
      highlights: -0.20,
      shadows: -0.10,
      whites: 0.15,
      blacks: -0.15,
      saturation: 0.0,
      vibrance: 1.0,
      clarity: 0.25,
      dehaze: 0.10,
      vignette: -0.20
    }
  },
  {
    id: "culto_celebracao",
    name: "Culto de Celebração",
    category: "Eventos",
    icon: "fa-fire text-red-500",
    description: "Cores vivas equilibradas e recuperação natural de telões.",
    params: {
      exposure_compensation: 0.10,
      temperature_kelvin: 5600,
      tint: 0.0,
      contrast: 1.08,
      highlights: -0.40,
      shadows: 0.20,
      whites: 0.0,
      blacks: 0.05,
      saturation: 1.05,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.05,
      vignette: -0.10
    }
  },
  {
    id: "cores_vibrantes_kids",
    name: "Cores Vibrantes (Kids)",
    category: "Eventos",
    icon: "fa-child-reaching text-pink-400",
    description: "Alegre e claro, ideal para o ministério infantil com cores puras.",
    params: {
      exposure_compensation: 0.15,
      temperature_kelvin: 5400,
      tint: -0.5,
      contrast: 1.05,
      highlights: -0.25,
      shadows: 0.30,
      whites: 0.10,
      blacks: 0.0,
      saturation: 1.15,
      vibrance: 1.0,
      clarity: 0.10,
      dehaze: 0.0,
      vignette: 0.0
    }
  },
  {
    id: "foco_no_altar",
    name: "Foco no Altar",
    category: "Pregação",
    icon: "fa-bullseye text-emerald-400",
    description: "Suave vinheta e equilíbrio focado em destacar o pregador.",
    params: {
      exposure_compensation: 0.05,
      temperature_kelvin: 5500,
      tint: 0.0,
      contrast: 1.08,
      highlights: -0.30,
      shadows: 0.10,
      whites: 0.0,
      blacks: 0.0,
      saturation: 1.0,
      vibrance: 1.0,
      clarity: 0.15,
      dehaze: 0.0,
      vignette: -0.35
    }
  },
  {
    id: "noturno_suave",
    name: "Noturno Suave",
    category: "Eventos",
    icon: "fa-moon text-indigo-400",
    description: "Ideal para ambientes muito escuros, sem forçar ruído.",
    params: {
      exposure_compensation: 0.20,
      temperature_kelvin: 5300,
      tint: 1.0,
      contrast: 1.02,
      highlights: -0.40,
      shadows: 0.45,
      whites: -0.10,
      blacks: 0.15,
      saturation: 0.95,
      vibrance: 1.0,
      clarity: 0.05,
      dehaze: 0.0,
      vignette: -0.05
    }
  }
];'''

html = re.sub(r'const DEFAULT_TEAM_PRESETS = \[.*?\];', new_presets, html, flags=re.DOTALL)
open('index.html', 'w', encoding='utf-8').write(html)
print('Done')
