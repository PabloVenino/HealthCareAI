import React from 'react';
import { HeartPulse } from 'lucide-react';

/**
 * Static top banner. Wrapped in React.memo — it takes no props, so it
 * will only ever render once and never re-render due to parent state changes.
 */
function AppHeaderComponent() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-50 px-6 py-4 shadow-sm">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-600 rounded-xl shadow-md shadow-indigo-600/20 text-white">
            <HeartPulse size={24} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-900 via-slate-700 to-indigo-600 bg-clip-text text-transparent">
              HealthCareAI
            </h1>
            <p className="text-xs text-slate-500 font-medium">Relatórios Epidemiológicos Inteligentes de SRAG</p>
          </div>
        </div>
      </div>
    </header>
  );
}

export const AppHeader = React.memo(AppHeaderComponent);
