import React, { useState, useCallback, useMemo } from 'react';
import { Database } from 'lucide-react';

export interface SqlViewerProps {
  executionLog: string[];
}

/**
 * Collapsible panel showing the generated SQL for transparency.
 * Owns its own open/closed state locally so toggling it doesn't cause
 * the rest of the dashboard to re-render. The toggle handler and the
 * extracted SQL string are both memoized.
 */
function SqlViewerComponent({ executionLog }: SqlViewerProps) {
  const [showSql, setShowSql] = useState(false);

  const toggleSql = useCallback(() => setShowSql((prev) => !prev), []);

  const sqlText = useMemo(() => {
    return (
      executionLog.find((log) => log.includes('SELECT * FROM srag'))?.replace('SQL Node: Executing query: ', '') ||
      'Consulta gerada dinamicamente via parâmetros.'
    );
  }, [executionLog]);

  return (
    <div className="border border-slate-200 rounded-2xl overflow-hidden bg-white">
      <button
        onClick={toggleSql}
        className="w-full flex items-center justify-between px-6 py-3 bg-slate-50 hover:bg-slate-100 text-slate-500 text-xs font-semibold cursor-pointer transition"
      >
        <span className="flex items-center gap-2">
          <Database size={14} />
          Visualizar Consulta SQL Utilizada (Transparência)
        </span>
        <span>{showSql ? 'Recolher [-]' : 'Expandir [+]'}</span>
      </button>
      {showSql && (
        <div className="p-4 bg-slate-900 border-t border-slate-800 font-mono text-[11px] text-indigo-300 overflow-x-auto">
          <pre>{sqlText}</pre>
        </div>
      )}
    </div>
  );
}

export const SqlViewer = React.memo(SqlViewerComponent);
