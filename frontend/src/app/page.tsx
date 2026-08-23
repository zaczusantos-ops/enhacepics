"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { DropzoneUpload } from "../components/DropzoneUpload";
import { ProcessingQueue } from "../components/ProcessingQueue";
import { BeforeAfterSlider } from "../components/BeforeAfterSlider";
import { ParameterInspector } from "../components/ParameterInspector";
import { PresetsBar } from "../components/PresetsBar";
import { HistogramViewer } from "../components/HistogramViewer";
import { QueueItem, ChurchPreset, ColorimetryParameters } from "../types";
import {
  checkApiHealth,
  fetchChurchPresets,
  analyzeAndProcessPhoto,
  reprocessWithCustomParams,
} from "../lib/api";
import { Sparkles, Layers, Sliders, AlertCircle, Shield, CheckCircle } from "lucide-react";

export default function Home() {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [presets, setPresets] = useState<ChurchPreset[]>([]);
  const [activePresetId, setActivePresetId] = useState<string | undefined>();
  const [geminiKey, setGeminiKey] = useState<string>("");
  const [apiStatus, setApiStatus] = useState<{ status: string; gemini_configured: boolean; model: string }>({
    status: "connecting",
    gemini_configured: false,
    model: "gemini-2.5-flash",
  });
  const [isProcessingAny, setIsProcessingAny] = useState<boolean>(false);
  const [isReprocessing, setIsReprocessing] = useState<boolean>(false);

  // Initialize and load stored settings
  useEffect(() => {
    const savedKey = localStorage.getItem("CHURCHPHOTO_GEMINI_KEY") || "";
    setGeminiKey(savedKey);

    checkApiHealth().then(setApiStatus);
    fetchChurchPresets().then(setPresets);
  }, []);

  const handleUpdateGeminiKey = (newKey: string) => {
    setGeminiKey(newKey);
    localStorage.setItem("CHURCHPHOTO_GEMINI_KEY", newKey);
  };

  const handleFilesSelected = (files: File[]) => {
    const newItems: QueueItem[] = files.map((file) => ({
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      file,
      previewUrl: URL.createObjectURL(file),
      status: "idle",
    }));

    setQueue((prev) => [...prev, ...newItems]);
    if (!selectedId && newItems.length > 0) {
      setSelectedId(newItems[0].id);
    }
  };

  const handleProcessItem = async (id: string) => {
    const item = queue.find((i) => i.id === id);
    if (!item || item.status === "processing" || item.status === "analyzing") return;

    // Update status to analyzing
    setQueue((prev) =>
      prev.map((i) => (i.id === id ? { ...i, status: "analyzing", errorMessage: undefined } : i))
    );

    try {
      const result = await analyzeAndProcessPhoto(item.file, geminiKey);

      setQueue((prev) =>
        prev.map((i) =>
          i.id === id
            ? {
                ...i,
                status: "completed",
                processedBase64: result.image_base64,
                originalBase64: result.original_base64 || i.previewUrl,
                metadata: result.metadata,
                analysis: result.analysis,
                currentParams: result.analysis,
              }
            : i
        )
      );
    } catch (err: any) {
      setQueue((prev) =>
        prev.map((i) =>
          i.id === id
            ? { ...i, status: "error", errorMessage: err.message || "Erro no processamento" }
            : i
        )
      );
    }
  };

  const handleProcessAll = async () => {
    setIsProcessingAny(true);
    const pendingItems = queue.filter((i) => i.status === "idle" || i.status === "error");

    for (const item of pendingItems) {
      await handleProcessItem(item.id);
    }
    setIsProcessingAny(false);
  };

  const handleRemoveItem = (id: string) => {
    setQueue((prev) => prev.filter((i) => i.id !== id));
    if (selectedId === id) {
      const remaining = queue.filter((i) => i.id !== id);
      setSelectedId(remaining.length > 0 ? remaining[0].id : null);
    }
  };

  const handleApplyCustomParams = async (updatedParams: ColorimetryParameters) => {
    if (!selectedItem || !selectedItem.file) return;

    setIsReprocessing(true);
    try {
      const result = await reprocessWithCustomParams(selectedItem.file, updatedParams);

      setQueue((prev) =>
        prev.map((i) =>
          i.id === selectedItem.id
            ? {
                ...i,
                processedBase64: result.image_base64,
                metadata: result.metadata,
                currentParams: updatedParams,
              }
            : i
        )
      );
    } catch (err: any) {
      console.error("Reprocessing failed:", err);
    } finally {
      setIsReprocessing(false);
    }
  };

  const handleSelectPreset = (preset: ChurchPreset) => {
    setActivePresetId(preset.id);
    if (selectedItem && selectedItem.status === "completed") {
      handleApplyCustomParams(preset.params);
    }
  };

  const selectedItem = queue.find((i) => i.id === selectedId);

  return (
    <div className="min-h-screen bg-church-950 text-slate-100 flex flex-col selection:bg-blue-600 selection:text-white">
      <Header
        isConfigured={apiStatus.gemini_configured}
        model={apiStatus.model}
        geminiKey={geminiKey}
        onUpdateKey={handleUpdateGeminiKey}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col gap-6 w-full">
        {/* Top Feature Bar & Church Presets */}
        <PresetsBar
          presets={presets}
          activePresetId={activePresetId}
          onSelectPreset={handleSelectPreset}
          disabled={!selectedItem || selectedItem.status !== "completed"}
        />

        {/* Workspace Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Upload & Queue */}
          <div className="lg:col-span-4 flex flex-col gap-5">
            <DropzoneUpload onFilesSelected={handleFilesSelected} />

            <ProcessingQueue
              items={queue}
              selectedId={selectedId}
              onSelectItem={setSelectedId}
              onRemoveItem={handleRemoveItem}
              onProcessItem={handleProcessItem}
              onProcessAll={handleProcessAll}
              isProcessingAny={isProcessingAny}
            />

            {/* Quick Tips Box */}
            <div className="rounded-2xl bg-church-900/60 border border-church-800 p-4 text-xs text-slate-400">
              <h4 className="font-semibold text-slate-200 flex items-center gap-1.5 mb-2">
                <Shield className="w-3.5 h-3.5 text-blue-400" />
                Regras de Proteção Fotográfica
              </h4>
              <ul className="space-y-1.5 list-disc list-inside text-slate-400 text-[11px] leading-relaxed">
                <li>Preservação determinística de tons de pele humana (melanina).</li>
                <li>Mitigação matemática de contaminação de LEDs cênicos.</li>
                <li>Sem modelos generativos faciais que alterem identidades.</li>
                <li>Processamento local de alta performance com OpenCV e Pillow.</li>
              </ul>
            </div>
          </div>

          {/* Right Column: Active Photo Inspector & Before/After Slider */}
          <div className="lg:col-span-8 flex flex-col gap-5">
            {selectedItem && selectedItem.processedBase64 ? (
              <>
                {/* Before / After Interactive Slider */}
                <BeforeAfterSlider
                  originalImage={selectedItem.originalBase64 || selectedItem.previewUrl}
                  processedImage={selectedItem.processedBase64}
                  filename={selectedItem.file.name}
                />

                {/* Histogram & Parameter Inspector Grid */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
                  <div className="md:col-span-4">
                    <HistogramViewer histogram={selectedItem.metadata?.histogram} />
                  </div>
                  <div className="md:col-span-8">
                    <ParameterInspector
                      parameters={selectedItem.currentParams || selectedItem.analysis!}
                      onApplyChanges={handleApplyCustomParams}
                      isReprocessing={isReprocessing}
                    />
                  </div>
                </div>
              </>
            ) : selectedItem ? (
              /* Selected item not yet processed */
              <div className="flex flex-col items-center justify-center p-12 rounded-2xl bg-church-900 border border-church-800 min-h-[480px] text-center">
                <div className="w-20 h-20 rounded-2xl bg-church-800 border border-church-700 overflow-hidden mb-4 shadow-xl">
                  <img
                    src={selectedItem.previewUrl}
                    alt={selectedItem.file.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-base font-bold text-white mb-1">{selectedItem.file.name}</h3>
                <p className="text-xs text-slate-400 max-w-sm mb-6">
                  Foto carregada na fila. Clique abaixo para iniciar a análise colorimétrica com o Gemini e processar os pixels.
                </p>
                <button
                  onClick={() => handleProcessItem(selectedItem.id)}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold shadow-xl shadow-blue-600/30 transition-all"
                >
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Processar Esta Fotografia</span>
                </button>
              </div>
            ) : (
              /* Empty state */
              <div className="flex flex-col items-center justify-center p-16 rounded-2xl bg-church-900/40 border border-church-800/80 border-dashed min-h-[480px] text-center">
                <div className="w-16 h-16 rounded-2xl bg-church-900 border border-church-800 flex items-center justify-center text-slate-600 mb-4">
                  <Layers className="w-8 h-8" />
                </div>
                <h3 className="text-base font-semibold text-slate-300 mb-1">
                  Nenhuma foto selecionada
                </h3>
                <p className="text-xs text-slate-500 max-w-xs">
                  Faça o upload de fotos de cultos no painel ao lado para iniciar a calibração profissional.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
