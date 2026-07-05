import React, { useMemo } from 'react';
import { FileText } from 'lucide-react';
import { parseMarkdown } from '../utils/markdownParser';

export interface ReportNarrativeProps {
  explanation: string;
}

/**
 * Renders the AI-generated narrative. parseMarkdown() rebuilds a React
 * node array from scratch on every call, so it's wrapped in useMemo keyed
 * on the explanation text — it only re-parses when the text itself changes.
 */
function ReportNarrativeComponent({ explanation }: ReportNarrativeProps) {
  const content = useMemo(() => parseMarkdown(explanation), [explanation]);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-sm">
      <div className="flex items-center gap-2.5 text-indigo-600 border-b border-slate-200 pb-3 mb-6">
        <FileText size={20} />
        <h2 className="text-lg font-bold text-slate-900">Relatório Consolidado pelo Agente IA</h2>
      </div>
      <div className="prose prose-indigo max-w-none bg-slate-50 border border-slate-200 p-6 rounded-2xl text-slate-800">
        {content}
      </div>
    </div>
  );
}

export const ReportNarrative = React.memo(ReportNarrativeComponent);
