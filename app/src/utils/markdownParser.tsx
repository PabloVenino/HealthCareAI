import React from 'react';

/**
 * A simple, custom Markdown -> React node parser used to render the
 * AI-generated report narrative without pulling in a full markdown library.
 *
 * This is a pure function (no hooks), so components that call it should
 * wrap the call in `useMemo(() => parseMarkdown(text), [text])` to avoid
 * re-parsing on every render.
 */
export function parseMarkdown(markdown: string): React.ReactNode[] {
  if (!markdown) return [];

  const lines = markdown.split('\n');
  return lines.map((line, idx) => {
    // Headers
    if (line.startsWith('### ')) {
      return <h4 key={idx} className="text-lg font-bold text-slate-800 mt-4 mb-2">{line.replace('### ', '')}</h4>;
    }
    if (line.startsWith('## ')) {
      return <h3 key={idx} className="text-xl font-bold text-slate-900 border-b border-slate-200 pb-2 mt-6 mb-3">{line.replace('## ', '')}</h3>;
    }
    if (line.startsWith('# ')) {
      return <h2 key={idx} className="text-2xl font-extrabold text-indigo-700 mt-8 mb-4">{line.replace('# ', '')}</h2>;
    }

    let cleanText = line;
    const isListItem = line.trim().startsWith('- ') || line.trim().startsWith('* ');
    if (isListItem) {
      cleanText = line.replace(/^\s*[-*]\s+/, '');
    }

    // Bold parsing: replace **text** with <strong>text</strong>
    let lineContent: React.ReactNode = cleanText;
    if (cleanText.includes('**')) {
      const parts = cleanText.split('**');
      lineContent = parts.map((part, i) => (i % 2 === 1 ? <strong key={i} className="font-semibold text-slate-900">{part}</strong> : part));
    }

    // List item
    if (isListItem) {
      return (
        <ul key={idx} className="list-disc list-inside ml-4 text-slate-700 my-1">
          <li>{lineContent}</li>
        </ul>
      );
    }

    // Paragraph
    if (line.trim() === '') {
      return <div key={idx} className="h-2" />;
    }

    return <p key={idx} className="text-slate-700 leading-relaxed my-2">{lineContent}</p>;
  });
}
