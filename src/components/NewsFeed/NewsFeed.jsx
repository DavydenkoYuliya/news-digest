import { useState } from 'react';
import { NewsCard } from './NewsCard';
import { getDateBoundaries, formatDateShort, formatDateLong } from '../../utils/dateUtils';

export function NewsFeed({ news, loading, filters, setFilter, isBookmarked, onToggleSave }) {
  const [prevOpen, setPrevOpen] = useState({ d1: true, d2: true });

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        Завантаження новин...
      </div>
    );
  }

  const { todayStart, yestStart, day2Start, day3Start } = getDateBoundaries();

  // Partition news into sections
  const todayNews = [];
  const yestNews = [];
  const day2News = [];

  news.forEach(n => {
    if (!n.date) { todayNews.push(n); return; }
    const t = n.date.getTime();
    if (t >= todayStart.getTime()) {
      todayNews.push(n);
    } else if (t >= yestStart.getTime()) {
      yestNews.push(n);
    } else if (t >= day2Start.getTime()) {
      day2News.push(n);
    }
  });

  const todayLabel = formatDateLong(new Date());
  const todayRange = `${formatDateShort(todayStart)} - ${formatDateShort(yestStart)}`;
  const yestRange = `${formatDateShort(yestStart)} - ${formatDateShort(day2Start)}`;
  const day2Range = `${formatDateShort(day2Start)} - ${formatDateShort(day3Start)}`;

  return (
    <>
      <div className="section-bar">
        <div className="section-title">
          <span className="dot" />
          Новини за останні 24 години ({todayRange})
          <span className="section-count">({todayNews.length})</span>
          <span className="current-date">📅 {todayLabel}</span>
        </div>
        <select
          className="sort-select"
          value={filters.sort}
          onChange={e => setFilter('sort', e.target.value)}
        >
          <option value="score">За релевантністю (Score)</option>
          <option value="date_new">За датою (найновіші)</option>
          <option value="date_old">За датою (найстаріші)</option>
          <option value="source">За джерелом</option>
        </select>
      </div>

      <div className="news-scroll">
        {todayNews.length === 0 && (
          <div className="loading" style={{ height: 120 }}>Новин за цей період не знайдено</div>
        )}
        {todayNews.map(item => (
          <NewsCard
            key={item.id}
            item={item}
            saved={isBookmarked(item.id)}
            onToggleSave={onToggleSave}
          />
        ))}

        {/* Previous sections */}
        <div className="prev-section">
          <PrevSection
            label={`Попередня доба (${yestRange})`}
            news={yestNews}
            open={prevOpen.d1}
            onToggle={() => setPrevOpen(p => ({ ...p, d1: !p.d1 }))}
            isBookmarked={isBookmarked}
            onToggleSave={onToggleSave}
          />
          <PrevSection
            label={`Попередні 2 доби (${day2Range})`}
            news={day2News}
            open={prevOpen.d2}
            onToggle={() => setPrevOpen(p => ({ ...p, d2: !p.d2 }))}
            isBookmarked={isBookmarked}
            onToggleSave={onToggleSave}
          />
        </div>
      </div>
    </>
  );
}

function PrevSection({ label, news, open, onToggle, isBookmarked, onToggleSave }) {
  const plural = (n) => {
    if (n % 10 === 1 && n % 100 !== 11) return 'новина';
    if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) return 'новини';
    return 'новин';
  };

  return (
    <>
      <div className="prev-header" onClick={onToggle}>
        <span className="prev-date">{label}</span>
        <span className="prev-count">{news.length} {plural(news.length)}</span>
        <span className={`chevron ${open ? 'open' : 'closed'}`}>▾</span>
      </div>
      {open && (
        <div className="prev-list">
          {news.map(item => (
            <NewsCard
              key={item.id}
              item={item}
              saved={isBookmarked(item.id)}
              onToggleSave={onToggleSave}
            />
          ))}
        </div>
      )}
    </>
  );
}
