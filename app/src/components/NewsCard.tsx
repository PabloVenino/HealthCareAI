import React from 'react';
import { ExternalLink } from 'lucide-react';
import type { ReportResponse } from '../services/api';

type NewsItem = ReportResponse['news'][number];

export interface NewsCardProps {
  item: NewsItem;
}

function NewsCardComponent({ item }: NewsCardProps) {
  return (
    <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl flex flex-col justify-between hover:border-slate-300 transition">
      <div>
        <div className="text-[10px] text-slate-400 font-semibold mb-1">{item.date}</div>
        <h3 className="text-xs font-bold text-slate-900 leading-snug line-clamp-2 mb-2">{item.title}</h3>
        <p className="text-[11px] text-slate-500 line-clamp-3 leading-relaxed mb-4">{item.summary}</p>
      </div>
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-[11px] text-indigo-600 hover:text-indigo-700 font-bold inline-flex items-center gap-1 mt-auto self-start"
      >
        Ver matéria completa
        <ExternalLink size={10} />
      </a>
    </div>
  );
}

export const NewsCard = React.memo(NewsCardComponent);
