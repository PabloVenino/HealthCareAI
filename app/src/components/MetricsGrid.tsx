import React, { useMemo } from 'react';
import { TrendingUp, Activity, Users } from 'lucide-react';
import type { ReportResponse } from '../services/api';
import { MetricCard } from './MetricCard';

type Metrics = ReportResponse['metrics'];

export interface MetricsGridProps {
  metrics: Metrics;
}

/**
 * Builds the 4 metric tiles from the raw metrics payload.
 * The card configs are derived with useMemo so a re-render of MetricsGrid
 * (e.g. triggered by a parent state change unrelated to metrics) doesn't
 * rebuild the array — and each MetricCard is itself memoized.
 */
function MetricsGridComponent({ metrics }: MetricsGridProps) {
  const cards = useMemo(
    () => [
      {
        key: 'mortality',
        label: 'Mortalidade Geral',
        value: `${(metrics.mortality_rate * 100).toFixed(2)}%`,
        subtext: `${metrics.total_deaths} óbitos / ${metrics.total_cases} casos`,
        icon: TrendingUp,
        iconColorClassName: 'text-red-400',
      },
      {
        key: 'icu',
        label: 'Internação em UTI',
        value: `${(metrics.icu_rate * 100).toFixed(2)}%`,
        subtext: `${metrics.total_icu} internados em UTI`,
        icon: Activity,
        iconColorClassName: 'text-indigo-400',
      },
      {
        key: 'vaccination',
        label: '% Vacinados (Internados)',
        labelTitle:
          'Proporção dos casos hospitalizados por SRAG que haviam recebido vacina COVID-19. NÃO é uma taxa populacional.',
        value: `${(metrics.hospitalized_vaccination_rate * 100).toFixed(2)}%`,
        subtext: `${metrics.total_vaccinated} internados vacinados (coorte hospitalar)`,
        icon: Users,
        iconColorClassName: 'text-emerald-400',
      },
      {
        key: 'increase',
        label: 'Aumento de Casos',
        value: `${(metrics.case_increase_rate * 100).toFixed(2)}%`,
        subtext: 'Comparação últimos 30 dias',
        icon: TrendingUp,
        iconColorClassName: 'text-amber-400',
      },
    ],
    [metrics]
  );

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((card) => (
        <MetricCard
          key={card.key}
          label={card.label}
          labelTitle={card.labelTitle}
          value={card.value}
          subtext={card.subtext}
          icon={card.icon}
          iconColorClassName={card.iconColorClassName}
        />
      ))}
    </div>
  );
}

export const MetricsGrid = React.memo(MetricsGridComponent);
