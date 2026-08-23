"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, Image as ImageIcon, Sparkles, AlertCircle, FileCode } from "lucide-react";

interface DropzoneUploadProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export const DropzoneUpload: React.FC<DropzoneUploadProps> = ({ onFilesSelected, disabled = false }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (disabled) return;
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files);
      onFilesSelected(filesArray);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      onFilesSelected(filesArray);
      // Reset input value so same files can be re-selected if needed
      e.target.value = "";
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => !disabled && fileInputRef.current?.click()}
      className={`relative group cursor-pointer rounded-2xl border-2 border-dashed transition-all p-8 flex flex-col items-center justify-center text-center overflow-hidden ${
        isDragOver
          ? "border-blue-500 bg-blue-500/10 scale-[1.01]"
          : "border-church-700 hover:border-blue-500/60 bg-church-900/60 hover:bg-church-850"
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/jpeg,image/png,image/webp,image/tiff,.cr2,.cr3,.nef,.arw,.dng,.orf,.raf"
        onChange={handleFileChange}
        className="hidden"
        disabled={disabled}
      />

      {/* Decorative ambient glow */}
      <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-64 h-24 bg-blue-500/10 blur-3xl pointer-events-none" />

      <div className="w-16 h-16 mb-4 rounded-2xl bg-church-800 border border-church-700 flex items-center justify-center text-blue-400 group-hover:scale-110 group-hover:text-blue-300 group-hover:border-blue-500/40 transition-all shadow-lg shadow-black/40">
        <UploadCloud className="w-8 h-8" />
      </div>

      <h3 className="text-lg font-semibold text-white mb-1">
        Arraste as fotos do culto ou clique para selecionar
      </h3>
      <p className="text-sm text-slate-400 max-w-md mb-4">
        Suporte a múltiplos arquivos simultâneos. Envie fotos de celulares, câmeras compactas ou arquivos brutos de DSLR.
      </p>

      {/* Supported Badges */}
      <div className="flex flex-wrap items-center justify-center gap-2">
        <span className="px-2.5 py-1 rounded-md bg-church-800 text-[11px] font-mono text-slate-300 border border-church-700">
          JPEG / PNG
        </span>
        <span className="px-2.5 py-1 rounded-md bg-church-800 text-[11px] font-mono text-slate-300 border border-church-700">
          Camera RAW (.CR2, .NEF, .ARW, .DNG)
        </span>
        <span className="px-2.5 py-1 rounded-md bg-blue-900/40 text-[11px] font-mono text-blue-300 border border-blue-700/50 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-amber-400" />
          Análise Gemini Vision
        </span>
      </div>
    </div>
  );
};
export default DropzoneUpload;
