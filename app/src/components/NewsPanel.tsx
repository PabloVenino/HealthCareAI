import React from 'react';
import { Newspaper } from 'lucide-react';
import type { ReportResponse } from '../services/api';
import { NewsCard } from './NewsCard';

export interface NewsPanelProps {
  news: ReportResponse['news'];
}

function NewsPanelComponent({ news }: NewsPanelProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <h2 className="text-md font-semibold text-indigo-600 mb-4 flex items-center gap-2">
        <Newspaper size={18} />
        Notícias e Fatores de Contexto
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {news.map((item, index) => (
          <NewsCard key={item.url ?? index} item={item} />
        ))}
      </div>
    </div>
  );
}

export const NewsPanel = React.memo(NewsPanelComponent);
