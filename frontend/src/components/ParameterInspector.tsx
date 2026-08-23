"use client";

import React, { useState, useEffect } from "react";
import { ColorimetryParameters } from "../types";
import {
  Sliders,
  Sun,
  Thermometer,
  Sparkles,
  RefreshCw,
  Palette,
  Zap,
  Crosshair,
  ShieldCheck,
  Camera,
} from "lucide-react";

interface ParameterInspectorProps {
  parameters: ColorimetryParameters;
  onApplyChanges: (updated: ColorimetryParameters) => void;
  isReprocessing?: boolean;
}

export const ParameterInspector: React.FC<ParameterInspectorProps> = ({
  parameters,
  onApplyChanges,
  isReprocessing = false,
}) => {
  const [localParams, setLocalParams] = useState<ColorimetryParameters>(parameters);
  const [activeTab, setActiveTab] = useState<1 | 2 | 3>(1);

  useEffect(() => {
    setLocalParams(parameters);
  }, [parameters]);

  const handleChange = (key: keyof ColorimetryParameters, value: any) => {
    setLocalParams((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const hasChanges = JSON.stringify(localParams) !== JSON.stringify(parameters);

  return (
    <div className="flex flex-col rounded-2xl bg-church-900 border border-church-800 p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-church-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">
            Painel DSLR em 3 Vertentes
          </h3>
        </div>

        {hasChanges && (
          <button
            onClick={() => onApplyChanges(localParams)}
            disabled={isReprocessing}
            className="flex items-center gap-1 px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all animate-pulse"
          >
            <RefreshCw className={`w-3 h-3 ${isReprocessing ? "animate-spin" : ""}`} />
            <span>Aplicar Ajustes</span>
          </button>
        )}
      </div>

      {/* Gemini Intelligence Summary */}
      <div className="mt-4 p-3 rounded-xl bg-church-950 border border-church-800 text-xs">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-1.5 text-blue-400 font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            Diagnóstico da Cena (Gemini 2.5 Pro):
          </div>
          <span className="text-[10px] font-mono text-amber-400">
            Foco: [{Math.round((localParams.focal_point_x || 0.5) * 100)}%, {Math.round((localParams.focal_point_y || 0.4) * 100)}%]
          </span>
        </div>
        <p className="text-slate-300 leading-relaxed font-mono text-[11px]">
          {localParams.analysis_summary}
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          <span className="px-2 py-0.5 rounded bg-blue-900/30 text-blue-300 border border-blue-800/40 text-[10px]">
            {localParams.detected_lighting_condition}
          </span>
          <span className="px-2 py-0.5 rounded bg-purple-900/30 text-purple-300 border border-purple-800/40 text-[10px]">
            {localParams.scene_moment || localParams.detected_scene_type}
          </span>
          <span className="px-2 py-0.5 rounded bg-emerald-900/30 text-emerald-300 border border-emerald-800/40 text-[10px]">
            f/{localParams.f_stop_simulation || 2.8} Bokeh
          </span>
        </div>
      </div>

      {/* 3 Vertente Tabs */}
      <div className="flex border-b border-church-800 mt-4 gap-2">
        <button
          onClick={() => setActiveTab(1)}
          className={`px-3 py-2 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
            activeTab === 1
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <Palette className="w-3.5 h-3.5" />
          <span>1. Cor & Luz</span>
        </button>

        <button
          onClick={() => setActiveTab(2)}
          className={`px-3 py-2 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
            activeTab === 2
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>2. Óptica & LEDs</span>
        </button>

        <button
          onClick={() => setActiveTab(3)}
          className={`px-3 py-2 text-xs font-bold border-b-2 flex items-center gap-1.5 transition-all ${
            activeTab === 3
              ? "border-blue-500 text-blue-400"
              : "border-transparent text-slate-400 hover:text-white"
          }`}
        >
          <Crosshair className="w-3.5 h-3.5" />
          <span>3. Foco & Bokeh</span>
        </button>
      </div>

      {/* Tab 1: Cor, Iluminação & Estilo */}
      {activeTab === 1 && (
        <div className="flex flex-col gap-4 mt-4">
          <div>
            <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
              <span className="flex items-center gap-1.5">
                <Sun className="w-3.5 h-3.5 text-amber-400" />
                Compensação de Exposição
              </span>
              <span className="font-mono text-blue-400 font-bold">
                {localParams.exposure_compensation > 0 ? `+${localParams.exposure_compensation}` : localParams.exposure_compensation} EV
              </span>
            </div>
            <input
              type="range"
              min="-2.0"
              max="2.0"
              step="0.05"
              value={localParams.exposure_compensation}
              onChange={(e) => handleChange("exposure_compensation", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
              <span className="flex items-center gap-1.5">
                <Thermometer className="w-3.5 h-3.5 text-orange-400" />
                Temperatura de Cor (Kelvin)
              </span>
              <span className="font-mono text-amber-400 font-bold">{localParams.temperature_kelvin}K</span>
            </div>
            <input
              type="range"
              min="2500"
              max="9000"
              step="50"
              value={localParams.temperature_kelvin}
              onChange={(e) => handleChange("temperature_kelvin", parseInt(e.target.value))}
              className="w-full h-1.5 bg-gradient-to-r from-amber-600 via-white to-blue-500 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
              <span>Matiz / Tint (Verde / Magenta)</span>
              <span className="font-mono text-pink-400 font-bold">{localParams.tint}</span>
            </div>
            <input
              type="range"
              min="-50"
              max="50"
              step="1"
              value={localParams.tint}
              onChange={(e) => handleChange("tint", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-gradient-to-r from-emerald-600 via-slate-700 to-fuchsia-600 rounded-lg appearance-none cursor-pointer accent-fuchsia-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
                <span>Recup. Realces (Telões)</span>
                <span className="font-mono text-blue-400">{Math.round(localParams.highlights_recovery * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={localParams.highlights_recovery}
                onChange={(e) => handleChange("highlights_recovery", parseFloat(e.target.value))}
                className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
                <span>Abertura de Sombras</span>
                <span className="font-mono text-blue-400">{Math.round(localParams.shadows_lift * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={localParams.shadows_lift}
                onChange={(e) => handleChange("shadows_lift", parseFloat(e.target.value))}
                className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
                <span>Contraste S-Curve</span>
                <span className="font-mono text-blue-400">{localParams.contrast}x</span>
              </div>
              <input
                type="range"
                min="0.8"
                max="1.5"
                step="0.02"
                value={localParams.contrast}
                onChange={(e) => handleChange("contrast", parseFloat(e.target.value))}
                className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
                <span>Vibração Tonal</span>
                <span className="font-mono text-emerald-400">{Math.round((localParams.vibrance || 1.05) * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.02"
                value={localParams.vibrance || 1.05}
                onChange={(e) => handleChange("vibrance", parseFloat(e.target.value))}
                className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Correção Óptica & LEDs */}
      {activeTab === 2 && (
        <div className="flex flex-col gap-4 mt-4">
          <div>
            <div className="flex justify-between text-xs font-semibold text-purple-300 mb-1">
              <span>Correção de Franjas Cromáticas (Aberração)</span>
              <span className="font-mono text-purple-400">{Math.round((localParams.chromatic_aberration_fix || 0.5) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.chromatic_aberration_fix || 0.5}
              onChange={(e) => handleChange("chromatic_aberration_fix", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-amber-300 mb-1">
              <span>Restauração de LEDs Estourados (Clipping)</span>
              <span className="font-mono text-amber-400">{Math.round((localParams.led_clipping_restoration || 0.6) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.led_clipping_restoration || 0.6}
              onChange={(e) => handleChange("led_clipping_restoration", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1">
              <span>Correção de Vinhetagem de Celular</span>
              <span className="font-mono text-blue-400">{Math.round((localParams.vignette_correction || 0.35) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.vignette_correction || 0.35}
              onChange={(e) => handleChange("vignette_correction", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-blue-300 mb-1">
              <span>Redução de Ruído Seletiva (Denoise ISO)</span>
              <span className="font-mono text-blue-400">{Math.round((localParams.selective_denoise || 0.3) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.selective_denoise || 0.3}
              onChange={(e) => handleChange("selective_denoise", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-amber-300 mb-1">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                Preservação Estrita de Tom de Pele (Melanina)
              </span>
              <span className="font-mono text-amber-400">{Math.round((localParams.skin_tone_protection_strength || 0.88) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.skin_tone_protection_strength || 0.88}
              onChange={(e) => handleChange("skin_tone_protection_strength", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>
        </div>
      )}

      {/* Tab 3: Foco & Bokeh DSLR */}
      {activeTab === 3 && (
        <div className="flex flex-col gap-4 mt-4">
          <div>
            <span className="text-xs text-slate-300 font-semibold mb-2 block">
              Abertura de Lente Similada (f/Stop):
            </span>
            <div className="grid grid-cols-6 gap-1 text-xs font-mono">
              {[1.4, 1.8, 2.8, 4.0, 5.6, 8.0].map((fVal) => (
                <button
                  key={fVal}
                  onClick={() => handleChange("f_stop_simulation", fVal)}
                  className={`py-1.5 rounded-lg font-bold border transition-all ${
                    Math.abs((localParams.f_stop_simulation || 2.8) - fVal) < 0.05
                      ? "bg-blue-600 border-blue-500 text-white shadow-md shadow-blue-600/30"
                      : "bg-church-950 border-church-800 text-slate-400 hover:text-white"
                  }`}
                >
                  f/{fVal}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-emerald-300 mb-1">
              <span>Suavidade do Bokeh (Profundidade)</span>
              <span className="font-mono text-emerald-400">{Math.round((localParams.bokeh_smoothness || 0.75) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.bokeh_smoothness || 0.75}
              onChange={(e) => handleChange("bokeh_smoothness", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-amber-300 mb-1">
              <span>Microcontraste & Nitidez no Sujeito</span>
              <span className="font-mono text-amber-400">{Math.round((localParams.subject_microcontrast || 0.75) * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="2.0"
              step="0.05"
              value={localParams.subject_microcontrast || 0.75}
              onChange={(e) => handleChange("subject_microcontrast", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};
export default ParameterInspector;
