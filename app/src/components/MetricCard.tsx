import React from 'react';
import type { LucideIcon } from 'lucide-react';

export interface MetricCardProps {
  label: string;
  labelTitle?: string;
  value: string;
  subtext: string;
  icon: LucideIcon;
  iconColorClassName: string;
}

/**
 * Generic metric tile. Memoized so that, inside MetricsGrid's .map(),
 * each card only re-renders if its own props changed — not when a
 * sibling card's data updates.
 */
function MetricCardComponent({ label, labelTitle, value, subtext, icon: Icon, iconColorClassName }: MetricCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
      <div className="flex items-center justify-between text-slate-500 text-xs mb-2">
        <span title={labelTitle}>{label}</span>
        <Icon size={14} className={iconColorClassName} />
      </div>
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="text-[10px] text-slate-400 mt-1">{subtext}</div>
    </div>
  );
}

export const MetricCard = React.memo(MetricCardComponent);
