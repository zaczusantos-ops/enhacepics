"use client";

import React, { useState, useEffect } from "react";
import { ColorimetryParameters } from "../types";
import {
  Sliders,
  Sun,
  Thermometer,
  Contrast,
  ShieldCheck,
  Zap,
  Sparkles,
  RefreshCw,
  Info,
  Layers,
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
            Painel de Calibração Colorimétrica
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
        <div className="flex items-center gap-1.5 text-blue-400 font-semibold mb-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Diagnóstico do Cérebro Analítico (Gemini):
        </div>
        <p className="text-slate-300 leading-relaxed font-mono text-[11px]">
          {localParams.analysis_summary}
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          <span className="px-2 py-0.5 rounded bg-blue-900/30 text-blue-300 border border-blue-800/40 text-[10px]">
            {localParams.detected_lighting_condition}
          </span>
          <span className="px-2 py-0.5 rounded bg-purple-900/30 text-purple-300 border border-purple-800/40 text-[10px]">
            {localParams.detected_scene_type}
          </span>
        </div>
      </div>

      {/* Sliders Grid */}
      <div className="flex flex-col gap-4 mt-5">
        {/* Exposure Compensation */}
        <div>
          <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
            <span className="flex items-center gap-1.5">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              Compensação de Exposição (EV)
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

        {/* Color Temperature (Kelvin) */}
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

        {/* Tint */}
        <div>
          <div className="flex justify-between text-xs font-medium text-slate-300 mb-1">
            <span>Coloração / Tint (Verde / Magenta)</span>
            <span className="font-mono text-slate-300 font-bold">{localParams.tint}</span>
          </div>
          <input
            type="range"
            min="-100"
            max="100"
            step="1"
            value={localParams.tint}
            onChange={(e) => handleChange("tint", parseFloat(e.target.value))}
            className="w-full h-1.5 bg-gradient-to-r from-emerald-600 via-slate-700 to-fuchsia-600 rounded-lg appearance-none cursor-pointer accent-fuchsia-500"
          />
        </div>

        {/* Highlights & Shadows */}
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

        {/* Contrast & Saturation */}
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
              <span>Saturação / Vibrance</span>
              <span className="font-mono text-blue-400">{localParams.saturation}x</span>
            </div>
            <input
              type="range"
              min="0.7"
              max="1.3"
              step="0.02"
              value={localParams.saturation}
              onChange={(e) => handleChange("saturation", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        </div>

        {/* Stage LED Suppression & Skin Protection */}
        <div className="p-3.5 rounded-xl bg-church-950/80 border border-church-800 flex flex-col gap-3">
          <div>
            <div className="flex justify-between text-xs font-semibold text-purple-300 mb-1">
              <span className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-purple-400" />
                Filtro de Atenuação de LEDs de Palco
              </span>
              <span className="font-mono text-purple-400">{Math.round(localParams.stage_led_tint_suppression * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.stage_led_tint_suppression}
              onChange={(e) => handleChange("stage_led_tint_suppression", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-amber-300 mb-1">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                Preservação Estrita de Tom de Pele (Melanina)
              </span>
              <span className="font-mono text-amber-400">{Math.round(localParams.skin_tone_protection_strength * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.skin_tone_protection_strength}
              onChange={(e) => handleChange("skin_tone_protection_strength", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>
        </div>

        {/* Denoise & Sharpening */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
              <span>Denoise Alto-ISO</span>
              <span className="font-mono text-blue-400">{Math.round(localParams.denoise_strength * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={localParams.denoise_strength}
              onChange={(e) => handleChange("denoise_strength", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div>
            <div className="flex justify-between text-[11px] font-medium text-slate-300 mb-1">
              <span>Nitidez Facial (Unsharp)</span>
              <span className="font-mono text-blue-400">{localParams.unsharp_mask_amount}x</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="2.0"
              step="0.1"
              value={localParams.unsharp_mask_amount}
              onChange={(e) => handleChange("unsharp_mask_amount", parseFloat(e.target.value))}
              className="w-full h-1.5 bg-church-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
export default ParameterInspector;
