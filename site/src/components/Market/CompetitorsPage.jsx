import { useRef } from 'react';

// Брифінг конкурентів — без змін: той самий competitor_brief.html, що й раніше, всередині вкладки.
export function CompetitorsPage() {
  const frame = useRef(null);
  const src = `${import.meta.env.BASE_URL}competitor_brief.html`;
  const fit = () => {
    try {
      const doc = frame.current.contentDocument;
      if (doc) frame.current.style.height = doc.documentElement.scrollHeight + 'px';
    } catch {}
  };
  return (
    <div className="competitors-page">
      <div className="comp-bar">
        <a href={src} target="_blank" rel="noopener noreferrer">Відкрити в окремій вкладці ↗</a>
      </div>
      <iframe ref={frame} className="briefframe" title="Брифінг по конкурентах" src={src} onLoad={fit} />
    </div>
  );
}
