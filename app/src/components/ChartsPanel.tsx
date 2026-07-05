import React from 'react';
import { type ReportResponse } from '../services/api';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

type Charts = ReportResponse['charts'];

export interface ChartsPanelProps {
  charts: Charts;
}

function ChartsPanelComponent({ charts }: ChartsPanelProps) {
  if (!charts) return null;

  const hasDaily = charts.daily_chart && charts.daily_chart.length > 0;
  const hasMonthly = charts.monthly_chart && charts.monthly_chart.length > 0;

  if (!hasDaily && !hasMonthly) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {hasDaily && (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-md flex flex-col">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">Casos Diários (Últimos 30 Dias)</h3>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={charts.daily_chart} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="DT_NOTIFIC" 
                  stroke="#64748b" 
                  fontSize={12} 
                  tickFormatter={(val) => {
                    const d = new Date(val);
                    return `${d.getDate()}/${d.getMonth()+1}`;
                  }}
                />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  labelFormatter={(val) => new Date(val).toLocaleDateString()}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  name="Casos"
                  dataKey="case_count" 
                  stroke="#6366f1" 
                  strokeWidth={3} 
                  dot={{ r: 4, strokeWidth: 2 }}
                  activeDot={{ r: 6 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      {hasMonthly && (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-md flex flex-col">
          <h3 className="text-lg font-semibold text-slate-800 mb-4 text-center">Casos Mensais (Últimos 12 Meses)</h3>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.monthly_chart} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="month" 
                  stroke="#64748b" 
                  fontSize={12}
                  tickFormatter={(val) => {
                    const [y, m] = val.split('-');
                    return `${m}/${y.slice(2)}`;
                  }}
                />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend />
                <Bar 
                  name="Casos"
                  dataKey="case_count" 
                  fill="#3b82f6" 
                  radius={[4, 4, 0, 0]} 
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

export const ChartsPanel = React.memo(ChartsPanelComponent);
