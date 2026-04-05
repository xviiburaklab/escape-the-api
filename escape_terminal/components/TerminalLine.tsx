import React from 'react';

interface TerminalLineProps {
  type: 'command' | 'response' | 'error' | 'success' | 'system';
  content: string | object;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export default function TerminalLine({ type, content }: TerminalLineProps) {
  let displayContent: React.ReactNode = content as string;

  if (typeof content === 'object') {
    const jsonStr = JSON.stringify(content, null, 2);
    // Sanitize then apply JSON highlighting
    displayContent = jsonStr.split('\n').map((line, i) => {
      const safeLine = escapeHtml(line);
      const formattedLine = safeLine
        .replace(/(&quot;.*?&quot;)(:)/g, '<span class="json-key">$1</span>$2')
        .replace(/:\s*(&quot;.*?&quot;)/g, ': <span class="json-string">$1</span>')
        .replace(/:\s*([0-9]+)/g, ': <span class="json-number">$1</span>')
        .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>');
      return (
        <React.Fragment key={i}>
          <span dangerouslySetInnerHTML={{ __html: formattedLine }} />
          <br />
        </React.Fragment>
      );
    });
  } else {
    displayContent = (content as string).split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        <br />
      </React.Fragment>
    ));
  }

  let colorClass = '';
  switch (type) {
    case 'command':
      colorClass = 'text-[#f5c842]';
      break;
    case 'error':
      colorClass = 'text-[#ff4444]';
      break;
    case 'success':
      colorClass = 'text-[#ff943c]';
      break;
    default:
      colorClass = 'text-[#fffefd]';
  }

  return (
    <div className={`mb-2 whitespace-pre-wrap ${colorClass}`}>
      {type === 'command' && <span className="mr-2">&gt;</span>}
      {displayContent}
    </div>
  );
}
