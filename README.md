# 📸 ChurchPhoto Pro - Sistema de Pós-Processamento Fotográfico para Cultos e Eventos

Aplicação web Full-Stack híbrida para pós-processamento fotográfico de alta fidelidade voltada para igrejas e eventos de adoração. O sistema combina o poder de raciocínio de visão computacional da **Google Gemini API** (Google AI Studio com Structured Outputs) com uma **Engine Determinística** matemática em Python (OpenCV, Pillow, NumPy, SciPy) e uma **Interface Moderna** (Next.js / React + Tailwind CSS) com comparador visual "Antes / Depois".

---

## 🌟 Principais Recursos

1. **Cérebro Analítico (Gemini Structured Outputs)**:
   - System Instruction treinada para colorimetria de cultos e eventos com iluminação cênica.
   - Retorno estritamente tipado em JSON via `response_schema` com Pydantic (`exposure_compensation`, `temperature_kelvin`, `tint`, `contrast`, `highlights_recovery`, `shadows_lift`, `saturation`, `stage_led_tint_suppression`, `blue_led_attenuation`, `red_magenta_attenuation`, `skin_tone_protection_strength`, `denoise_strength`, `unsharp_mask_amount`).
2. **Engine Determinística de Imagem**:
   - **Balanço de Branco Físico**: Calibração Kelvin (2500K a 9000K) e Tint via curvas Planckianas.
   - **Curvas de Tom & Faixa Dinâmica**: Recuperação de realces estourados em telões LED e elevação suave de sombras na congregação.
   - **Atenuação de LEDs Cênicos**: Filtro seletivo nos canais de croma para canhões PAR LED azuis, cianos, magentas e vermelhos.
   - **Proteção Estrita de Tom de Pele (Melanina)**: Segmentação em espaços de cor HSV e YCrCb/Lab para manter os rostos dos membros naturais e saudáveis, sem distorções generativas que alterem identidades.
   - **Denoise Alto-ISO & Unsharp Masking**: Filtro bilateral para ruído de baixa luz e máscara de nitidez adaptativa.
   - **Suporte a Formatos RAW**: Carregamento de JPEG, PNG, TIFF e leitura de arquivos RAW de câmeras DSLR (.CR2, .NEF, .ARW, .DNG).
3. **Interface de Usuário Profissional**:
   - Comparador Antes / Depois interativo com modo Split-Slider, Lado a Lado e Zoom 200%.
   - Fila de processamento em lote com status em tempo real e badges de diagnóstico.
   - Painel de telemetria e sliders para ajustes finos em tempo real.
   - Presets específicos para cultos (Culto Contemporâneo, Tradicional, Louvor Intimista, Evento Externo).

---

## 🔑 Configuração de Deploy Key (GitHub)

Para versionar este projeto diretamente no repositório GitHub com a chave SSH gerada:

- **Chave Pública**:
```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHlJhj5gYfeaR190Yp8e4v/p/HOsORE6CZLX1iWwAO3f deploy-enhancepics-church-photo
```

No GitHub:
1. Acesse seu repositório $\rightarrow$ **Settings** $\rightarrow$ **Deploy keys**.
2. Clique em **Add deploy key**, cole a chave acima e marque **Allow write access**.

---

## 🚀 Como Executar

### 1. Instalação das Dependências (Backend Python)
```bash
pip install -r backend/requirements.txt
```

### 2. Configuração da Chave da Gemini API (Opcional)
Crie um arquivo `.env` a partir do `.env.example` ou insira a chave diretamente no botão da interface web:
```env
GEMINI_API_KEY=AIzaSy_SUA_CHAVE_AQUI
```

### 3. Iniciar o Servidor & Estúdio Web
Execute o script PowerShell:
```powershell
.\start.ps1
```
Ou diretamente com o Uvicorn:
```bash
python -m uvicorn backend.app.main:app --port 8000 --reload
```
Acesse no navegador:
👉 **http://localhost:8000** (Interface Web Completa)  
👉 **http://localhost:8000/docs** (Documentação Interativa Swagger/OpenAPI)

---

## 📁 Estrutura de Diretórios

```text
enhancepics/
├── backend/
│   ├── app/
│   │   ├── config.py                # Configurações e modelos Gemini
│   │   ├── main.py                  # API FastAPI e endpoints
│   │   ├── schemas/
│   │   │   └── colorimetry.py       # Pydantic Schemas tipados
│   │   ├── services/
│   │   │   └── gemini_analyzer.py   # Análise Gemini com Structured JSON
│   │   └── engine/
│   │       ├── processor.py         # Pipeline unificado determinístico
│   │       ├── color_curves.py      # Kelvin, Tint, Exposure, S-Curves
│   │       ├── stage_lighting.py    # Atenuação de LEDs cênicos de palco
│   │       ├── skin_tones.py        # Proteção de tons de pele humana
│   │       ├── denoise_sharpen.py   # Bilateral Denoise e Unsharp Mask
│   │       └── raw_loader.py        # Leitor de múltiplos formatos e RAW
│   ├── static/
│   │   └── index.html               # Estúdio Web com Comparador Antes/Depois
│   ├── requirements.txt
│   └── tests/
│       ├── test_engine.py
│       └── test_gemini_schema.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── BeforeAfterSlider.tsx # Componente Comparador Antes/Depois
│   │   │   ├── DropzoneUpload.tsx    # Drag-and-drop de múltiplos uploads
│   │   │   ├── ProcessingQueue.tsx   # Fila de processamento em lote
│   │   │   ├── ParameterInspector.tsx# Sliders para ajuste fino
│   │   │   ├── PresetsBar.tsx        # Presets específicos de culto
│   │   │   ├── HistogramViewer.tsx   # Histograma RGB
│   │   │   └── Header.tsx
│   │   ├── lib/
│   │   │   └── api.ts
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
├── .env.example
├── README.md
└── start.ps1
```

---

## 🧪 Testes Automatizados

Para rodar a suíte de testes unitários:
```bash
python -m backend.tests.test_engine
python -m backend.tests.test_gemini_schema
```
