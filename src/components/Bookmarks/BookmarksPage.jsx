import { useState, useMemo } from 'react';
import { NewsCard } from '../NewsFeed/NewsCard';

function formatGroupDate(date) {
  if (!date) return 'Без дати';
  return date.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' });
}

function toDate(val) {
  if (!val) return null;
  if (val instanceof Date) return val;
  const d = new Date(val);
  return isNaN(d.getTime()) ? null : d;
}

function getDateKey(item) {
  const d = toDate(item.date);
  if (!d) return '0000-00-00';
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function getItemDate(item) {
  return toDate(item.date);
}

export function BookmarksPage({ bookmarkList, isBookmarked, onToggleSave }) {
  const [sort, setSort] = useState('saved_desc');

  const sorted = useMemo(() => {
    const list = [...bookmarkList];
    if (sort === 'saved_desc') return list.sort((a, b) => b.savedAt - a.savedAt);
    if (sort === 'saved_asc')  return list.sort((a, b) => a.savedAt - b.savedAt);
    if (sort === 'date_new')   return list.sort((a, b) => (toDate(b.date)?.getTime() ?? 0) - (toDate(a.date)?.getTime() ?? 0));
    if (sort === 'date_old')   return list.sort((a, b) => (toDate(a.date)?.getTime() ?? 0) - (toDate(b.date)?.getTime() ?? 0));
    if (sort === 'score')      return list.sort((a, b) => b.score - a.score);
    return list;
  }, [bookmarkList, sort]);

  // Group by publication date (day)
  const groups = useMemo(() => {
    if (sort === 'score') {
      // No grouping for score sort
      return [{ key: 'all', label: null, items: sorted }];
    }
    const map = new Map();
    sorted.forEach(item => {
      const key = getDateKey(item);
      if (!map.has(key)) map.set(key, { key, date: getItemDate(item), items: [] });
      map.get(key).items.push(item);
    });
    return Array.from(map.values());
  }, [sorted, sort]);

  if (bookmarkList.length === 0) {
    return (
      <div className="content">
        <div className="bookmarks-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          Збережених новин немає.
          <span style={{ fontSize: 13 }}>Натисніть ⭐ на картці новини, щоб зберегти.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="content">
      <div className="section-bar">
        <div className="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="#F59E0B" stroke="#F59E0B" strokeWidth="1">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          Закладки
          <span className="section-count">({bookmarkList.length})</span>
        </div>
        <select
          className="sort-select"
          value={sort}
          onChange={e => setSort(e.target.value)}
        >
          <option value="saved_desc">За датою збереження (нові)</option>
          <option value="saved_asc">За датою збереження (старі)</option>
          <option value="date_new">За датою публікації (нові)</option>
          <option value="date_old">За датою публікації (старі)</option>
          <option value="score">За релевантністю (Score)</option>
        </select>
      </div>

      <div className="bookmarks-page">
        {groups.map(group => (
          <div key={group.key}>
            {group.label !== null && (
              <div className="bm-date-header">
                <span className="bm-date-label">
                  📅 {formatGroupDate(group.date)}
                </span>
                <span className="bm-date-count">{group.items.length}</span>
              </div>
            )}
            {group.items.map(item => (
              <NewsCard
                key={item.id}
                item={item}
                saved={isBookmarked(item.id)}
                onToggleSave={onToggleSave}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
