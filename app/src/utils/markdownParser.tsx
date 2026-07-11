import React from 'react';

/** URL regex — matches bare http/https links in text. */
const URL_REGEX = /https?:\/\/[^\s"'<>)]+/g;

/**
 * Truncates a URL string to `maxLen` characters, appending "..." if needed.
 */
function truncateUrl(url: string, maxLen = 40): string {
  return url.length > maxLen ? url.slice(0, maxLen) + '…' : url;
}

/**
 * Splits a plain text string on bare URLs, returning a mixed array of
 * strings and clickable <a> elements with truncated labels.
 */
function renderTextWithLinks(text: string, keyPrefix: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  const re = new RegExp(URL_REGEX.source, 'g');

  while ((match = re.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    const url = match[0];
    parts.push(
      <a
        key={`${keyPrefix}-url-${match.index}`}
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        title={url}
        className="text-indigo-600 hover:text-indigo-800 underline underline-offset-2 break-all"
      >
        {truncateUrl(url)}
      </a>
    );
    lastIndex = match.index + url.length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length === 1 && typeof parts[0] === 'string' ? parts[0] : <>{parts}</>;
}

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

    // Bold + URL parsing: split on **…**, then scan each plain segment for URLs.
    let lineContent: React.ReactNode;
    if (cleanText.includes('**')) {
      const parts = cleanText.split('**');
      lineContent = parts.map((part, i) =>
        i % 2 === 1 ? (
          <strong key={i} className="font-semibold text-slate-900">
            {part}
          </strong>
        ) : (
          <React.Fragment key={i}>
            {renderTextWithLinks(part, `${idx}-${i}`)}
          </React.Fragment>
        )
      );
    } else {
      lineContent = renderTextWithLinks(cleanText, `${idx}`);
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
