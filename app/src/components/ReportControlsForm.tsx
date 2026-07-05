import React from 'react';
import { Calendar, MapPin, Search, Loader2, Compass } from 'lucide-react';

export interface ReportControlsFormProps {
  startDate: string;
  endDate: string;
  uf: string;
  isPending: boolean;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  onUfChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

/**
 * Fully structured filter form: date range + UF select.
 * The free-text "natural language query" input has been intentionally
 * removed — every report is now generated purely from these structured
 * filters.
 *
 * Memoized: as long as the parent passes stable callbacks (via useCallback)
 * and only updates the primitive values that actually changed, this form
 * won't re-render when unrelated App state (like the mutation result) changes.
 */
function ReportControlsFormComponent({
  startDate,
  endDate,
  uf,
  isPending,
  onStartDateChange,
  onEndDateChange,
  onUfChange,
  onSubmit,
}: ReportControlsFormProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <h2 className="text-md font-semibold text-indigo-600 mb-4 flex items-center gap-2">
        <Compass size={18} />
        Parâmetros de Análise
      </h2>

      <form onSubmit={onSubmit} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-2">Data Inicial</label>
            <div className="relative">
              <Calendar size={14} className="absolute left-3 top-3 text-slate-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => onStartDateChange(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 focus:border-indigo-500 rounded-xl text-slate-900 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-2">Data Final</label>
            <div className="relative">
              <Calendar size={14} className="absolute left-3 top-3 text-slate-400" />
              <input
                type="date"
                value={endDate}
                onChange={(e) => onEndDateChange(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 focus:border-indigo-500 rounded-xl text-slate-900 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-2">Estado (UF)</label>
          <div className="relative">
            <MapPin size={14} className="absolute left-3 top-3.5 text-slate-400" />
            <select
              value={uf}
              onChange={(e) => onUfChange(e.target.value)}
              className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 focus:border-indigo-500 rounded-xl text-slate-900 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 transition appearance-none"
            >
              <option value="ALL">Brasil (Todos os Estados)</option>
              <option value="SP">São Paulo (SP)</option>
              <option value="RJ">Rio de Janeiro (RJ)</option>
              <option value="MG">Minas Gerais (MG)</option>
              <option value="RS">Rio Grande do Sul (RS)</option>
              <option value="PR">Paraná (PR)</option>
              <option value="BA">Bahia (BA)</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={isPending}
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-300 rounded-xl font-semibold text-sm text-white flex items-center justify-center gap-2 transition shadow-md shadow-indigo-600/10 cursor-pointer"
        >
          {isPending ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Processando Agente...
            </>
          ) : (
            <>
              <Search size={16} />
              Gerar Relatório Analítico
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export const ReportControlsForm = React.memo(ReportControlsFormComponent);
