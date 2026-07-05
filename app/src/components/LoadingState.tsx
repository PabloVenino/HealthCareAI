import React from 'react';
import { HeartPulse } from 'lucide-react';

function LoadingStateComponent() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[400px]">
      <div className="relative flex items-center justify-center">
        <div className="h-16 w-16 rounded-full border-t-2 border-b-2 border-indigo-500 animate-spin"></div>
        <HeartPulse size={24} className="absolute text-indigo-500 animate-pulse" />
      </div>
      <h3 className="text-md font-semibold text-slate-700 mt-6">Orquestrando Ferramentas...</h3>
      <p className="text-xs text-slate-500 text-center max-w-xs mt-1">
        Calculando taxas epidemiológicas de forma determinística e buscando dados reais da rede InfoGripe.
      </p>
    </div>
  );
}

export const LoadingState = React.memo(LoadingStateComponent);
