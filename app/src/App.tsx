import React, { useState, useCallback, useMemo } from 'react';
import { useMutation } from '@tanstack/react-query';
import { fetchReport, type ReportResponse, type ReportRequest } from './services/api';
import { Toaster, toast } from 'sonner';

import { AppHeader } from './components/AppHeader';
import { AppFooter } from './components/AppFooter';
import { ReportControlsForm } from './components/ReportControlsForm';
import { ExecutionLogPanel } from './components/ExecutionLogPanel';
import { ErrorBanner } from './components/ErrorBanner';
import { EmptyState } from './components/EmptyState';
import { LoadingState } from './components/LoadingState';
import { ResultsDashboard } from './components/ResultsDashboard';

// UF display names used to build a human-readable summary that is sent to
// the backend in place of the old free-text query field.
const UF_LABELS: Record<string, string> = {
  ALL: 'todos os estados do Brasil',
  SP: 'São Paulo (SP)',
  RJ: 'Rio de Janeiro (RJ)',
  MG: 'Minas Gerais (MG)',
  RS: 'Rio Grande do Sul (RS)',
  PR: 'Paraná (PR)',
  BA: 'Bahia (BA)',
};

function App() {
  const [startDate, setStartDate] = useState('2025-05-01');
  const [endDate, setEndDate] = useState('2025-10-30');
  const [uf, setUf] = useState('SP');

  const mutation = useMutation<ReportResponse, Error, ReportRequest>({
    mutationFn: fetchReport,
    onError: (err) => {
      toast.error(err.message, { duration: 5000 });
    }
  });

  // Stable setter callbacks passed down to the memoized form so it never
  // sees a new function reference across renders.
  const handleStartDateChange = useCallback((value: string) => setStartDate(value), []);
  const handleEndDateChange = useCallback((value: string) => setEndDate(value), []);
  const handleUfChange = useCallback((value: string) => setUf(value), []);

  // The structured filters are the single source of truth now. We still
  // derive a short descriptive string for the backend's `query` field so
  // existing report-generation logic keeps working without needing a
  // free-text input from the user.
  const derivedQuery = useMemo(() => {
    const ufLabel = UF_LABELS[uf] ?? uf;
    return `Analisar casos de SRAG em ${ufLabel} de ${startDate} até ${endDate}`;
  }, [uf, startDate, endDate]);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      mutation.mutate({
        query: derivedQuery,
        filters: {
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          uf: uf || undefined,
        },
      });
    },
    [mutation, derivedQuery, startDate, endDate, uf]
  );

  const results = mutation.data;
  const isPending = mutation.isPending;
  const error = mutation.error;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Toaster position="top-right" richColors />
      <AppHeader />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Control Panel */}
        <section className="lg:col-span-4 flex flex-col space-y-6">
          <ReportControlsForm
            startDate={startDate}
            endDate={endDate}
            uf={uf}
            isPending={isPending}
            onStartDateChange={handleStartDateChange}
            onEndDateChange={handleEndDateChange}
            onUfChange={handleUfChange}
            onSubmit={handleSubmit}
          />

          <ExecutionLogPanel executionLog={results?.execution_log} isPending={isPending} />
        </section>

        {/* Right Dashboard Area */}
        <section className="lg:col-span-8 flex flex-col space-y-6">
          {error && <ErrorBanner message={error.message} />}

          {!results && !isPending && <EmptyState />}

          {isPending && <LoadingState />}

          {results && !isPending && <ResultsDashboard results={results} />}
        </section>
      </main>

      <AppFooter />
    </div>
  );
}

export default App;
