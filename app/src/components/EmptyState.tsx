import React from 'react';
import { HeartPulse } from 'lucide-react';

function EmptyStateComponent() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center border border-dashed border-slate-300 rounded-3xl p-12 bg-slate-50">
      <HeartPulse size={48} className="text-slate-300 mb-4" />
      <h3 className="text-lg font-semibold text-slate-600">Pronto para Coleta</h3>
      <p className="text-sm text-slate-500 text-center max-w-sm mt-1">
        Configure os parâmetros à esquerda e clique em gerar para orquestrar os dados do DATASUS e notícias de saúde.
      </p>
    </div>
  );
}

export const EmptyState = React.memo(EmptyStateComponent);
