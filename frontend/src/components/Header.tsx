"use client";

import React, { useState } from "react";
import { Camera, Sparkles, Key, CheckCircle, AlertCircle, Settings2 } from "lucide-react";

interface HeaderProps {
  isConfigured: boolean;
  model: string;
  geminiKey: string;
  onUpdateKey: (key: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  isConfigured,
  model,
  geminiKey,
  onUpdateKey,
}) => {
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [tempKey, setTempKey] = useState(geminiKey);

  const handleSave = () => {
    onUpdateKey(tempKey);
    setShowKeyModal(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-church-950/80 backdrop-blur-xl border-b border-church-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">
                ChurchPhoto <span className="text-blue-400">Pro</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-blue-900/40 text-blue-300 text-[10px] font-mono border border-blue-700/50">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Pós-Processamento Fotográfico para Cultos & Eventos
            </p>
          </div>
        </div>

        {/* Status & Settings */}
        <div className="flex items-center gap-3">
          {/* Gemini Status Pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-church-900 border border-church-800 text-xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-300 font-medium">Gemini Vision:</span>
            <span className="font-mono text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {model || "gemini-2.5-flash"}
            </span>
          </div>

          {/* API Key Modal Button */}
          <button
            onClick={() => {
              setTempKey(geminiKey);
              setShowKeyModal(true);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-church-900 hover:bg-church-850 border border-church-800 text-xs font-medium text-slate-300 hover:text-white transition-all"
            title="Configurar Chave Gemini API"
          >
            <Key className="w-3.5 h-3.5 text-blue-400" />
            <span className="hidden md:inline">Chave Gemini</span>
          </button>
        </div>
      </div>

      {/* API Key Modal */}
      {showKeyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-md bg-church-900 border border-church-800 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-2 mb-3">
              <Key className="w-5 h-5 text-blue-400" />
              <h3 className="text-base font-bold text-white">Chave da Gemini API (Google AI Studio)</h3>
            </div>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              Insira sua chave de API para habilitar a análise em tempo real com o modelo Gemini Vision.
              A chave permanece segura e salva localmente no seu navegador.
            </p>
            <input
              type="password"
              placeholder="Cole sua chave AIzaSy..."
              value={tempKey}
              onChange={(e) => setTempKey(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-church-950 border border-church-800 text-white font-mono text-xs focus:outline-none focus:border-blue-500 mb-5"
            />
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setShowKeyModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-church-800 transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/25 transition-all"
              >
                Salvar Chave
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
export default Header;
