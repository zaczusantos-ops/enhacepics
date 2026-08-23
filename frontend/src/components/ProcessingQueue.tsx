"use client";

import React from "react";
import { QueueItem } from "../types";
import {
  CheckCircle2,
  Clock,
  Loader2,
  AlertTriangle,
  Download,
  Trash2,
  Sparkles,
  ArrowRight,
  Eye,
} from "lucide-react";

interface ProcessingQueueProps {
  items: QueueItem[];
  selectedId: string | null;
  onSelectItem: (id: string) => void;
  onRemoveItem: (id: string) => void;
  onProcessItem: (id: string) => void;
  onProcessAll: () => void;
  isProcessingAny: boolean;
}

export const ProcessingQueue: React.FC<ProcessingQueueProps> = ({
  items,
  selectedId,
  onSelectItem,
  onRemoveItem,
  onProcessItem,
  onProcessAll,
  isProcessingAny,
}) => {
  if (items.length === 0) return null;

  const completedCount = items.filter((i) => i.status === "completed").length;

  return (
    <div className="flex flex-col rounded-2xl bg-church-900 border border-church-800 p-5 shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-church-800">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            Fila de Processamento em Lote
            <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 text-xs font-mono">
              {completedCount}/{items.length} Prontas
            </span>
          </h3>
          <p className="text-xs text-slate-400">
            Selecione uma foto da fila para visualizar a comparação Antes/Depois e telemetria.
          </p>
        </div>

        <button
          onClick={onProcessAll}
          disabled={isProcessingAny || completedCount === items.length}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
        >
          {isProcessingAny ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Processando Lote...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Processar Todas</span>
            </>
          )}
        </button>
      </div>

      {/* Item List */}
      <div className="flex flex-col gap-2.5 mt-4 max-h-72 overflow-y-auto pr-1">
        {items.map((item) => {
          const isSelected = item.id === selectedId;

          return (
            <div
              key={item.id}
              onClick={() => onSelectItem(item.id)}
              className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? "bg-blue-950/40 border-blue-500/80 shadow-md shadow-blue-900/20"
                  : "bg-church-950/60 border-church-800 hover:border-church-700 hover:bg-church-850"
              }`}
            >
              {/* Left thumbnail & title */}
              <div className="flex items-center gap-3 min-w-0">
                <div className="relative w-12 h-12 rounded-lg bg-church-800 overflow-hidden shrink-0 border border-church-700">
                  <img
                    src={item.processedBase64 || item.previewUrl}
                    alt={item.file.name}
                    className="w-full h-full object-cover"
                  />
                  {item.status === "completed" && (
                    <div className="absolute top-0.5 right-0.5 bg-emerald-500 rounded-full p-0.5">
                      <CheckCircle2 className="w-2.5 h-2.5 text-white" />
                    </div>
                  )}
                </div>

                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-semibold text-white truncate">
                    {item.file.name}
                  </span>
                  <div className="flex items-center gap-2 text-[11px] text-slate-400">
                    <span>{(item.file.size / (1024 * 1024)).toFixed(1)} MB</span>
                    {item.metadata && (
                      <>
                        <span>•</span>
                        <span className="font-mono text-slate-500">
                          {item.metadata.width}x{item.metadata.height}
                        </span>
                        <span>•</span>
                        <span className="text-emerald-400 font-mono">
                          {item.metadata.execution_time_ms}ms
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Center status badge */}
              <div className="hidden sm:flex items-center gap-2">
                {item.status === "idle" && (
                  <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 text-[11px] font-medium flex items-center gap-1 border border-slate-700">
                    <Clock className="w-3 h-3" /> Aguardando
                  </span>
                )}
                {item.status === "analyzing" && (
                  <span className="px-2.5 py-1 rounded-md bg-blue-900/50 text-blue-300 text-[11px] font-medium flex items-center gap-1 border border-blue-700 animate-pulse">
                    <Loader2 className="w-3 h-3 animate-spin" /> Analisando Gemini
                  </span>
                )}
                {item.status === "processing" && (
                  <span className="px-2.5 py-1 rounded-md bg-amber-900/50 text-amber-300 text-[11px] font-medium flex items-center gap-1 border border-amber-700 animate-pulse">
                    <Loader2 className="w-3 h-3 animate-spin" /> Renderizando Pixels
                  </span>
                )}
                {item.status === "completed" && (
                  <span className="px-2.5 py-1 rounded-md bg-emerald-950/60 text-emerald-300 text-[11px] font-medium flex items-center gap-1 border border-emerald-700/60">
                    <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Pronta em HD
                  </span>
                )}
                {item.status === "error" && (
                  <span className="px-2.5 py-1 rounded-md bg-red-950/60 text-red-300 text-[11px] font-medium flex items-center gap-1 border border-red-700/60">
                    <AlertTriangle className="w-3 h-3 text-red-400" /> Erro
                  </span>
                )}
              </div>

              {/* Right actions */}
              <div className="flex items-center gap-1.5 ml-2">
                {item.status === "idle" && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onProcessItem(item.id);
                    }}
                    className="p-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white transition-all"
                    title="Processar Foto"
                  >
                    <Sparkles className="w-4 h-4" />
                  </button>
                )}

                {item.status === "completed" && item.processedBase64 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const link = document.createElement("a");
                      link.href = item.processedBase64!;
                      link.download = `enhanced_${item.file.name}`;
                      link.click();
                    }}
                    className="p-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white transition-all"
                    title="Baixar Foto Tratada"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                )}

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveItem(item.id);
                  }}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-950/40 transition-all"
                  title="Remover da Fila"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default ProcessingQueue;
