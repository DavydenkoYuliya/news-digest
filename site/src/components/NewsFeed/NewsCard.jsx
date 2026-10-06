import { useState, useEffect, useRef } from 'react';
import { getScoreClass, capitalize, cleanSource, firstCountries } from '../../utils/constants';
import { formatTime, formatDateShort } from '../../utils/dateUtils';

const DOMAIN_ICONS = {
  logistics: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M1 3h15v13H1z"/><path d="M16 8h4l3 3v5h-7V8z"/>
      <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
    </svg>
  ),
  geo: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/>
      <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
    </svg>
  ),
  energy: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  ),
  agro: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 22V8M5 12l7-4 7 4M9 6l3-4 3 4"/>
    </svg>
  ),
  finance: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
      <polyline points="16 7 22 7 22 13"/>
    </svg>
  ),
  regulatory: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
    </svg>
  ),
  prices: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
      <path d="M7 7h.01"/>
    </svg>
  ),
  trade: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/>
      <polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/>
    </svg>
  ),
  weather: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 16.58A5 5 0 0018 7h-1.26A8 8 0 104 15.25"/>
      <path d="M8 19v2M8 13v2M16 19v2M16 13v2M12 21v2M12 15v2"/>
    </svg>
  ),
  health: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v6M9 11h6"/>
    </svg>
  ),
  strike: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      <path d="M12 9v4M12 17h.01"/>
    </svg>
  ),
  other: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/><path d="M8 12h8"/>
    </svg>
  ),
};

const InfoIcon = () => (
  <svg className="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
  </svg>
);

export function NewsCard({ item, highlight }) {
  const [showDetails, setShowDetails] = useState(false);
  const rowRef = useRef(null);
  const isTarget = highlight != null && highlight === item.n;
  useEffect(() => { if (isTarget && rowRef.current) rowRef.current.scrollIntoView({ block: 'center' }); }, [isTarget]);
  // іконка напряму задається в config.yaml (taxonomy.domains); невідома назва → «other»
  const domainKey = DOMAIN_ICONS[item.domainKey] ? item.domainKey : 'other';
  const icon = DOMAIN_ICONS[domainKey];
  const scoreClass = getScoreClass(item.score);
  const timeStr = item.date ? formatTime(item.date) : '';
  const dateStr = item.date ? formatDateShort(item.date) : '';

  const commodityTag = item.commodity &&
    !item.commodity.toLowerCase().includes('всі') ? item.commodity.split(',')[0].trim() : null;
  const countryTags = firstCountries(item.country, commodityTag ? 1 : 2);
  const extraTags = [commodityTag, ...countryTags].filter(Boolean).slice(0, 2);

  const scoreDisplay = Number.isInteger(item.score) ? item.score : item.score.toFixed(1);
  const sourceName = cleanSource(item.source);

  const scoreBadge = (
    <div className={`score-badge ${scoreClass}`}>{scoreDisplay}</div>
  );

  const timeDate = [timeStr, dateStr].filter(Boolean).join(' · ');

  const metaBlock = (
    <div className="row-meta">
      {timeDate && <span>{timeDate}</span>}
      <span className="row-source">{sourceName}</span>
    </div>
  );

  return (
    <div ref={rowRef} id={item.n ? `news-${item.n}` : undefined} className={`news-row${isTarget ? ' flash' : ''}`}>

      {/* ── LEFT COLUMN: icon + (mobile) score, meta, save ── */}
      <div className="card-left">
        <div className={`domain-icon di-${domainKey}`}>{icon}</div>
        {/* Shown only on mobile */}
        <div className="card-left-meta">
          {scoreBadge}
          {metaBlock}
        </div>
      </div>

      {/* ── RIGHT COLUMN: title + tags + (desktop) score, meta, save ── */}
      <div className="card-right">
        <div className="row-title-block">
          <div className="row-title-wrapper">
            <a
              href={item.url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="row-title"
              title={[item.summary, (item.rssText && item.rssText.length > 100 ? item.rssText : item.detailed)].filter(Boolean).join('\n\n')}
            >
              {item.n ? <span className="news-num">#{item.n}</span> : null}{item.title}
            </a>
            {item.detailed && (
              <button
                className="info-btn"
                onClick={() => setShowDetails(!showDetails)}
                title="Показати деталі"
              >
                ℹ️
              </button>
            )}
          </div>

          {/* Detailed summary (shown when clicked) */}
          {item.detailed && showDetails && (
            <div className="row-detailed">
              {item.detailed}
            </div>
          )}
        </div>

        <div className="row-bottom">
          <div className="row-tags">
            <span className="tag tag-domain">{capitalize(item.domain)}</span>
            {extraTags.map((t, i) => (
              <span key={i} className="tag">{t}</span>
            ))}
          </div>
        </div>

        {/* Shown only on desktop */}
        <div className="card-right-meta">
          <div className="tooltip-trigger">
            {scoreBadge}
            <InfoIcon />
            <div className="tooltip">
              Score {scoreDisplay} — релевантність для бізнесу МХП.
              {item.detailed && <><br/><br/>{item.detailed}</>}
            </div>
          </div>
          {metaBlock}
        </div>
      </div>

    </div>
  );
}
