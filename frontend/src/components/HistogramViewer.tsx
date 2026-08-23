"use client";

import React from "react";
import { Activity } from "lucide-react";

interface HistogramViewerProps {
  histogram?: {
    r: number[];
    g: number[];
    b: number[];
  };
}

export const HistogramViewer: React.FC<HistogramViewerProps> = ({ histogram }) => {
  if (!histogram || !histogram.r || histogram.r.length === 0) return null;

  return (
    <div className="flex flex-col p-4 rounded-2xl bg-church-900 border border-church-800 shadow-xl">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-300">
          <Activity className="w-3.5 h-3.5 text-blue-400" />
          Histograma de Cores RGB
        </div>
        <div className="flex items-center gap-3 text-[10px] font-mono">
          <span className="flex items-center gap-1 text-red-400">
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> R
          </span>
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> G
          </span>
          <span className="flex items-center gap-1 text-blue-400">
            <span className="w-2 h-2 rounded-full bg-blue-500 inline-block" /> B
          </span>
        </div>
      </div>

      {/* Waveform Chart Canvas Representation */}
      <div className="relative w-full h-20 bg-church-950 rounded-xl overflow-hidden p-1 border border-church-800 flex items-end">
        <svg className="w-full h-full" viewBox={`0 0 ${histogram.r.length} 100`} preserveAspectRatio="none">
          {/* Red path */}
          <polyline
            fill="rgba(239, 68, 68, 0.15)"
            stroke="#ef4444"
            strokeWidth="1.2"
            points={histogram.r.map((val, idx) => `${idx},${100 - val}`).join(" ") + ` ${histogram.r.length},100 0,100`}
          />
          {/* Green path */}
          <polyline
            fill="rgba(34, 197, 94, 0.15)"
            stroke="#22c55e"
            strokeWidth="1.2"
            points={histogram.g.map((val, idx) => `${idx},${100 - val}`).join(" ") + ` ${histogram.g.length},100 0,100`}
          />
          {/* Blue path */}
          <polyline
            fill="rgba(59, 130, 246, 0.15)"
            stroke="#3b82f6"
            strokeWidth="1.2"
            points={histogram.b.map((val, idx) => `${idx},${100 - val}`).join(" ") + ` ${histogram.b.length},100 0,100`}
          />
        </svg>
      </div>

      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1 px-1">
        <span>0 (Sombras)</span>
        <span>128 (Médios)</span>
        <span>255 (Realces)</span>
      </div>
    </div>
  );
};
export default HistogramViewer;
