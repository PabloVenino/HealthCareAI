import React from 'react';
import type { ReportResponse } from '../services/api';
import { MetricsGrid } from './MetricsGrid';
import { ChartsPanel } from './ChartsPanel';
import { SqlViewer } from './SqlViewer';
import { ReportNarrative } from './ReportNarrative';
import { NewsPanel } from './NewsPanel';

export interface ResultsDashboardProps {
  results: ReportResponse;
}

/**
 * Groups every "results" section. Memoized on the `results` object as a
 * whole — since react-query returns a new object per successful mutation,
 * this only re-renders when a new report actually comes back, not on
 * every keystroke in the filters form.
 */
function ResultsDashboardComponent({ results }: ResultsDashboardProps) {
  return (
    <div className="space-y-6 animate-fade-in">
      {results.metrics && <MetricsGrid metrics={results.metrics} />}

      {results.charts && <ChartsPanel charts={results.charts} />}

      <SqlViewer executionLog={results.execution_log} />

      <ReportNarrative explanation={results.explanation} />

      {results.news && results.news.length > 0 && <NewsPanel news={results.news} />}
    </div>
  );
}

export const ResultsDashboard = React.memo(ResultsDashboardComponent);
