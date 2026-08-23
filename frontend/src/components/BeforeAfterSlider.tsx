"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import {
  SplitSquareVertical,
  Columns,
  Eye,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Sparkles,
  Download,
  RotateCcw,
} from "lucide-react";

interface BeforeAfterSliderProps {
  originalImage: string;
  processedImage: string;
  filename?: string;
  aspectRatio?: string;
  className?: string;
  focalPoint?: { x: number; y: number };
  fStop?: number;
  onFocalPointChange?: (x: number, y: number) => void;
}

export const BeforeAfterSlider: React.FC<BeforeAfterSliderProps> = ({
  originalImage,
  processedImage,
  filename = "culto_processado.jpg",
  aspectRatio = "16/9",
  className = "",
  focalPoint = { x: 0.5, y: 0.4 },
  fStop = 2.8,
  onFocalPointChange,
}) => {
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<"slider" | "side-by-side" | "hold">("slider");
  const [isHoldingOriginal, setIsHoldingOriginal] = useState<boolean>(false);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const panStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current || viewMode !== "slider") return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPosition(percentage);
    },
    [viewMode]
  );

  const handleTouchMove = useCallback(
    (e: TouchEvent) => {
      if (!isDragging) return;
      handleMove(e.touches[0].clientX);
    },
    [isDragging, handleMove]
  );

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (isDragging) {
        handleMove(e.clientX);
      } else if (isPanning) {
        const dx = e.clientX - panStartRef.current.x;
        const dy = e.clientY - panStartRef.current.y;
        setPanOffset((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
        panStartRef.current = { x: e.clientX, y: e.clientY };
      }
    },
    [isDragging, isPanning, handleMove]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setIsPanning(false);
  }, []);

  useEffect(() => {
    if (isDragging || isPanning) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      window.addEventListener("touchmove", handleTouchMove);
      window.addEventListener("touchend", handleMouseUp);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleMouseUp);
    };
  }, [isDragging, isPanning, handleMouseMove, handleMouseUp, handleTouchMove]);

  const handleDownload = () => {
    const link = document.createElement("a");
    link.href = processedImage;
    link.download = `enhanced_${filename}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleZoom = () => {
    if (zoomLevel === 1) {
      setZoomLevel(2);
    } else {
      setZoomLevel(1);
      setPanOffset({ x: 0, y: 0 });
    }
  };

  return (
    <div className={`flex flex-col rounded-2xl bg-church-900 border border-church-800 shadow-2xl overflow-hidden ${className}`}>
      {/* Top Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-church-950/80 border-b border-church-800 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Comparador de Precisão
          </span>
          <span className="text-xs text-slate-500 font-mono hidden sm:inline">
            ({filename})
          </span>
        </div>

        <div className="flex items-center gap-1.5 bg-church-900 p-1 rounded-xl border border-church-800">
          <button
            onClick={() => { setViewMode("slider"); setZoomLevel(1); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === "slider"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-white hover:bg-church-800"
            }`}
            title="Divisão Deslizante (Split Slider)"
          >
            <SplitSquareVertical className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Divisão</span>
          </button>

          <button
            onClick={() => { setViewMode("side-by-side"); setZoomLevel(1); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === "side-by-side"
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "text-slate-400 hover:text-white hover:bg-church-800"
            }`}
            title="Comparação Lado a Lado"
          >
            <Columns className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Lado a Lado</span>
          </button>

          <button
            onMouseDown={() => setIsHoldingOriginal(true)}
            onMouseUp={() => setIsHoldingOriginal(false)}
            onMouseLeave={() => setIsHoldingOriginal(false)}
            onTouchStart={() => setIsHoldingOriginal(true)}
            onTouchEnd={() => setIsHoldingOriginal(false)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isHoldingOriginal
                ? "bg-amber-600 text-white shadow-md shadow-amber-500/20"
                : "text-slate-400 hover:text-white hover:bg-church-800"
            }`}
            title="Segure para ver o Antes original"
          >
            <Eye className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Segurar Original</span>
          </button>

          <div className="h-4 w-[1px] bg-church-800 mx-1" />

          <button
            onClick={toggleZoom}
            className={`p-1.5 rounded-lg text-xs font-medium transition-all ${
              zoomLevel > 1 ? "bg-church-800 text-blue-400" : "text-slate-400 hover:text-white"
            }`}
            title={zoomLevel > 1 ? "Resetar Zoom" : "Zoom 200% (Inspecionar Nitidez)"}
          >
            {zoomLevel > 1 ? <ZoomOut className="w-4 h-4" /> : <ZoomIn className="w-4 h-4" />}
          </button>

          <button
            onClick={handleDownload}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20 transition-all ml-1"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Baixar HD</span>
          </button>
        </div>
      </div>

      {/* Main Image Viewport */}
      <div
        ref={containerRef}
        className="relative w-full h-[520px] bg-church-950 select-none overflow-hidden cursor-crosshair flex items-center justify-center"
        onClick={(e) => {
          if (!containerRef.current || isDragging || !onFocalPointChange) return;
          const rect = containerRef.current.getBoundingClientRect();
          const clickX = Math.max(0.1, Math.min(0.9, (e.clientX - rect.left) / rect.width));
          const clickY = Math.max(0.1, Math.min(0.9, (e.clientY - rect.top) / rect.height));
          onFocalPointChange(clickX, clickY);
        }}
        onMouseDown={(e) => {
          if (zoomLevel > 1) {
            setIsPanning(true);
            panStartRef.current = { x: e.clientX, y: e.clientY };
          }
        }}
      >
        {/* MODE 1: SPLIT SLIDER */}
        {viewMode === "slider" && (
          <div
            className="relative w-full h-full flex items-center justify-center transition-transform duration-75"
            style={{
              transform: `scale(${zoomLevel}) translate(${panOffset.x / zoomLevel}px, ${panOffset.y / zoomLevel}px)`,
              transformOrigin: "center center",
            }}
          >
            {/* Background: Processed Image (Depois) */}
            <img
              src={processedImage}
              alt="Depois (Tratada)"
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
            />

            {/* Foreground Clip: Original Image (Antes) */}
            <div
              className="absolute inset-0 overflow-hidden pointer-events-none"
              style={{
                clipPath: `polygon(0 0, ${sliderPosition}% 0, ${sliderPosition}% 100%, 0 100%)`,
              }}
            >
              <img
                src={originalImage}
                alt="Antes (Original)"
                className="absolute inset-0 w-full h-full object-contain"
              />
            </div>

            {/* Interactive Focal Reticle */}
            <div
              className="absolute z-20 pointer-events-none transition-all duration-200"
              style={{
                left: `${(focalPoint.x * 100).toFixed(1)}%`,
                top: `${(focalPoint.y * 100).toFixed(1)}%`,
                transform: "translate(-50%, -50%)",
              }}
            >
              <div className="w-10 h-10 rounded-full border-2 border-amber-400 bg-amber-400/10 shadow-[0_0_15px_rgba(245,158,11,0.6)] flex items-center justify-center animate-pulse">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-300" />
              </div>
              <span className="absolute top-11 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-md bg-black/80 border border-amber-400/40 text-[9px] font-mono text-amber-300 whitespace-nowrap shadow-lg">
                f/{fStop} · Foco DSLR
              </span>
            </div>

            {/* Draggable Divider Handle */}
            <div
              className="absolute top-0 bottom-0 z-30 cursor-ew-resize flex items-center justify-center group"
              style={{ left: `${sliderPosition}%`, transform: "translateX(-50%)" }}
              onMouseDown={(e) => {
                e.stopPropagation();
                setIsDragging(true);
              }}
              onTouchStart={(e) => {
                e.stopPropagation();
                setIsDragging(true);
              }}
            >
              {/* Line */}
              <div className="w-[2px] h-full bg-white/80 shadow-[0_0_10px_rgba(0,0,0,0.8)] group-hover:w-[3px] group-hover:bg-blue-400 transition-colors" />

              {/* Central Badge / Knob */}
              <div className="absolute w-9 h-9 rounded-full bg-church-900/90 border-2 border-white/90 shadow-xl flex items-center justify-center text-white backdrop-blur-sm group-hover:scale-110 group-hover:border-blue-400 transition-all">
                <div className="flex gap-1">
                  <div className="w-0.5 h-3 bg-white rounded-full" />
                  <div className="w-0.5 h-3 bg-white rounded-full" />
                </div>
              </div>
            </div>

            {/* Floating Labels */}
            <div className="absolute bottom-4 left-4 z-10 pointer-events-none">
              <span className="px-2.5 py-1 rounded-md bg-black/70 border border-white/10 text-[11px] font-mono font-medium text-slate-300 backdrop-blur-md uppercase tracking-wider shadow-lg">
                Antes (Original)
              </span>
            </div>

            <div className="absolute bottom-4 right-4 z-10 pointer-events-none">
              <span className="px-2.5 py-1 rounded-md bg-blue-600/80 border border-blue-400/30 text-[11px] font-mono font-semibold text-white backdrop-blur-md uppercase tracking-wider shadow-lg flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-300" />
                Depois (ChurchPhoto Pro)
              </span>
            </div>
          </div>
        )}

        {/* MODE 2: SIDE-BY-SIDE */}
        {viewMode === "side-by-side" && (
          <div className="grid grid-cols-2 w-full h-full gap-2 p-2 bg-church-950">
            <div className="relative rounded-xl overflow-hidden bg-church-900 border border-church-800 flex items-center justify-center">
              <img src={originalImage} alt="Antes (Original)" className="w-full h-full object-contain" />
              <span className="absolute bottom-3 left-3 px-2.5 py-1 rounded-md bg-black/70 border border-white/10 text-[10px] font-mono font-medium text-slate-300 backdrop-blur-md uppercase">
                Antes (Original)
              </span>
            </div>
            <div className="relative rounded-xl overflow-hidden bg-church-900 border border-church-800 flex items-center justify-center">
              <img src={processedImage} alt="Depois (Tratada)" className="w-full h-full object-contain" />
              <span className="absolute bottom-3 right-3 px-2.5 py-1 rounded-md bg-blue-600/90 border border-blue-400/30 text-[10px] font-mono font-semibold text-white backdrop-blur-md uppercase flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5 text-amber-300" />
                Depois (Tratada)
              </span>
            </div>
          </div>
        )}

        {/* MODE 3: HOLD ORIGINAL */}
        {viewMode === "hold" && (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              src={isHoldingOriginal ? originalImage : processedImage}
              alt="Visualização"
              className="w-full h-full object-contain transition-opacity duration-150"
            />
            <div className="absolute top-4 left-4 z-10 pointer-events-none">
              <span className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold uppercase tracking-wider backdrop-blur-md shadow-lg ${
                isHoldingOriginal ? "bg-amber-600 text-white" : "bg-blue-600 text-white"
              }`}>
                {isHoldingOriginal ? "Exibindo Original (Antes)" : "Exibindo Tratada (Depois)"}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="px-4 py-2 bg-church-950 border-t border-church-800 flex items-center justify-between text-[11px] text-slate-400">
        <span>Arraste o cursor horizontalmente para revelar a calibração colorimétrica.</span>
        <span className="font-mono text-slate-500">Divisão: {Math.round(sliderPosition)}%</span>
      </div>
    </div>
  );
};
export default BeforeAfterSlider;
