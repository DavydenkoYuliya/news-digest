import { getScoreClass, getDomainKey, capitalize, cleanSource, firstCountries } from '../../utils/constants';
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
};

const StarEmpty = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);
const StarFull = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);
const InfoIcon = () => (
  <svg className="info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
  </svg>
);

export function NewsCard({ item, saved, onToggleSave }) {
  const domainKey = item.domainKey || getDomainKey(item.domain);
  const icon = DOMAIN_ICONS[domainKey] || DOMAIN_ICONS.geo;
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

  const saveBtn = (
    <button
      className={`save-btn${saved ? ' saved' : ''}`}
      title={saved ? 'Збережено' : 'Зберегти'}
      onClick={() => onToggleSave(item)}
    >
      {saved ? <StarFull /> : <StarEmpty />}
    </button>
  );

  return (
    <div className={`news-row${saved ? ' saved' : ''}`}>

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
        <a
          href={item.url || '#'}
          target="_blank"
          rel="noopener noreferrer"
          className="row-title"
          title={item.summary}
        >
          {item.title}
        </a>

        <div className="row-bottom">
          <div className="row-tags">
            <span className="tag tag-domain">{capitalize(item.domain)}</span>
            {extraTags.map((t, i) => (
              <span key={i} className="tag">{t}</span>
            ))}
          </div>
          {/* Star visible only on mobile */}
          <button
            className={`save-btn save-btn-mob${saved ? ' saved' : ''}`}
            title={saved ? 'Збережено' : 'Зберегти'}
            onClick={() => onToggleSave(item)}
          >
            {saved ? <StarFull /> : <StarEmpty />}
          </button>
        </div>

        {/* Shown only on desktop */}
        <div className="card-right-meta">
          <div className="tooltip-trigger">
            {scoreBadge}
            <InfoIcon />
            <div className="tooltip">
              Score {scoreDisplay} — релевантність для бізнесу МХП.
              {item.summary && <><br/><br/>{item.summary}</>}
            </div>
          </div>
          {metaBlock}
          {saveBtn}
        </div>
      </div>

    </div>
  );
}
