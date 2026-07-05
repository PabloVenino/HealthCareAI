import React from 'react';
import { Database, Loader2 } from 'lucide-react';

export interface ExecutionLogPanelProps {
  executionLog?: string[];
  isPending: boolean;
}

/**
 * Renders the LangGraph audit trail. Memoized so it only re-renders when
 * the log array reference or the pending flag actually changes, not on
 * every keystroke in the filter form.
 */
function ExecutionLogPanelComponent({ executionLog, isPending }: ExecutionLogPanelProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex-1 flex flex-col min-h-[300px]">
      <h2 className="text-md font-semibold text-slate-700 mb-4 flex items-center gap-2 border-b border-slate-200 pb-2">
        <Database size={18} className="text-slate-400" />
        Logs de Execução (Auditabilidade)
      </h2>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2 text-xs font-mono text-slate-600 max-h-[400px]">
        {isPending && (
          <div className="flex items-center gap-2 text-indigo-600 py-1">
            <Loader2 size={12} className="animate-spin" />
            <span>LangGraph executando nós em segundo plano...</span>
          </div>
        )}
        {executionLog ? (
          executionLog.map((log, index) => (
            <div key={index} className="flex gap-2 items-start border-l border-indigo-300 pl-3 py-0.5">
              <span className="text-indigo-500 font-bold">↳</span>
              <span className="leading-relaxed">{log}</span>
            </div>
          ))
        ) : (
          !isPending && (
            <p className="text-slate-400 italic text-center mt-8">Nenhum log disponível. Execute uma consulta para iniciar.</p>
          )
        )}
      </div>
    </div>
  );
}

export const ExecutionLogPanel = React.memo(ExecutionLogPanelComponent);
