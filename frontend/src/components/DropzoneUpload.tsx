"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, Image as ImageIcon, Camera, Sparkles } from "lucide-react";

interface DropzoneUploadProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export const DropzoneUpload: React.FC<DropzoneUploadProps> = ({ onFilesSelected, disabled = false }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

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

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      onFilesSelected(filesArray);
      e.target.value = "";
    }
  };

  return (
    <div className="w-full flex flex-col gap-3">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInput}
        multiple
        accept="image/*,.cr2,.cr3,.nef,.arw,.dng"
        className="hidden"
        disabled={disabled}
      />
      <input
        type="file"
        ref={cameraInputRef}
        onChange={handleFileInput}
        accept="image/*"
        capture="environment"
        className="hidden"
        disabled={disabled}
      />

      {/* Direct Mobile Upload & Camera Buttons */}
      <div className="flex flex-col sm:flex-row gap-2.5">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="flex-1 py-3.5 px-4 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer disabled:opacity-50"
        >
          <ImageIcon className="w-5 h-5" />
          <span>Escolher da Galeria</span>
        </button>

        <button
          type="button"
          onClick={() => cameraInputRef.current?.click()}
          disabled={disabled}
          className="sm:w-auto py-3.5 px-4 rounded-2xl bg-church-800 hover:bg-church-750 border border-church-700 text-slate-200 font-semibold text-sm flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer disabled:opacity-50"
        >
          <Camera className="w-5 h-5 text-blue-400" />
          <span className="sm:hidden">Tirar Foto</span>
          <span className="hidden sm:inline">Câmera</span>
        </button>
      </div>

      {/* Desktop Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`hidden sm:flex relative group cursor-pointer rounded-2xl border-2 border-dashed transition-all p-6 flex-col items-center justify-center text-center overflow-hidden ${
          isDragOver
            ? "border-blue-500 bg-blue-500/10 scale-[1.01]"
            : "border-church-700 hover:border-blue-500/60 bg-church-900/60 hover:bg-church-850"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <div className="w-12 h-12 mb-2 rounded-xl bg-church-800 border border-church-700 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-all shadow-md">
          <UploadCloud className="w-6 h-6" />
        </div>
        <span className="text-xs font-semibold text-white mb-1">
          Ou arraste as fotos aqui
        </span>
        <p className="text-[11px] text-slate-400">
          Suporte a JPEG, PNG, WebP e arquivos Camera RAW
        </p>
      </div>
    </div>
  );
};

export default DropzoneUpload;
