import React from 'react';
import { AlertTriangle } from 'lucide-react';

export interface ErrorBannerProps {
  message?: string;
}

function ErrorBannerComponent({ message }: ErrorBannerProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex items-start gap-3 text-red-700">
      <AlertTriangle className="text-red-500 mt-0.5 shrink-0" size={20} />
      <div>
        <h3 className="font-bold text-sm">Erro de Processamento</h3>
        <p className="text-xs text-red-600 mt-1">{message || 'Falha ao conectar com o servidor backend.'}</p>
      </div>
    </div>
  );
}

export const ErrorBanner = React.memo(ErrorBannerComponent);
