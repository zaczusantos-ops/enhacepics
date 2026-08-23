"use client";

import React from "react";
import { ChurchPreset, ColorimetryParameters } from "../types";
import { Sparkles, Flame, Church, Music, Sun } from "lucide-react";

interface PresetsBarProps {
  presets: ChurchPreset[];
  activePresetId?: string;
  onSelectPreset: (preset: ChurchPreset) => void;
  disabled?: boolean;
}

export const PresetsBar: React.FC<PresetsBarProps> = ({
  presets,
  activePresetId,
  onSelectPreset,
  disabled = false,
}) => {
  const getPresetIcon = (id: string) => {
    switch (id) {
      case "culto_contemporaneo":
        return <Flame className="w-4 h-4 text-amber-400" />;
      case "culto_tradicional":
        return <Church className="w-4 h-4 text-blue-400" />;
      case "louvor_adoracao":
        return <Music className="w-4 h-4 text-purple-400" />;
      case "evento_externo":
        return <Sun className="w-4 h-4 text-emerald-400" />;
      default:
        return <Sparkles className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="flex flex-col gap-2 p-4 rounded-2xl bg-church-900 border border-church-800 shadow-xl">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Presets Específicos de Culto
        </span>
        <span className="text-[11px] text-slate-500">1-Clique para calibrar</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 mt-1">
        {presets.map((preset) => {
          const isActive = preset.id === activePresetId;

          return (
            <button
              key={preset.id}
              onClick={() => onSelectPreset(preset)}
              disabled={disabled}
              className={`flex flex-col text-left p-3 rounded-xl border transition-all ${
                isActive
                  ? "bg-blue-950/60 border-blue-500 shadow-md shadow-blue-500/20"
                  : "bg-church-950/80 border-church-800 hover:border-church-700 hover:bg-church-850"
              } ${disabled ? "opacity-40 cursor-not-allowed" : ""}`}
            >
              <div className="flex items-center gap-2 mb-1">
                {getPresetIcon(preset.id)}
                <span className="text-xs font-bold text-white truncate">
                  {preset.name}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-2">
                {preset.description}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
export default PresetsBar;
