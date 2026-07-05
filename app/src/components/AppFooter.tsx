import React from 'react';

function AppFooterComponent() {
  return (
    <footer className="border-t border-slate-200 bg-white/80 text-center py-6 text-xs text-slate-500 font-medium">
      <div className="max-w-7xl mx-auto px-6">
        <p>© 2026 HealthCareAI. Dados abertos DATASUS SIVEP-Gripe e orquestração determinística de agentes.</p>
      </div>
    </footer>
  );
}

export const AppFooter = React.memo(AppFooterComponent);
