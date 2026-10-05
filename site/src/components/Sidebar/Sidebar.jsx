import { useState } from 'react';
import { capitalize } from '../../utils/constants';

export function Sidebar({ filters, options, setFilter, toggleMulti, setMulti, reset, totalCount, inDrawer }) {
  const { search, minScore, domains, categories, countries, commodities } = filters;

  const scorePercent = ((minScore - 1) / 9) * 100;

  const inner = (
    <div className="sidebar-card">
        <div className="sidebar-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46"/>
          </svg>
          Фільтри
        </div>

        <div className="filter-meta">
          <span className="found-count">Знайдено: {totalCount} новин</span>
          <button className="reset-btn" onClick={reset}>Скинути фільтри</button>
        </div>

        <input
          className="search-box"
          placeholder="Пошук за ключовими словами..."
          value={search}
          onChange={e => setFilter('search', e.target.value)}
        />

        <div className="filter-group">
          <div className="filter-label">Score (релевантність)</div>
          <div className="range-row">
            <span className="range-val">{minScore}</span>
            <input
              type="range"
              min="1"
              max="10"
              value={minScore}
              style={{
                background: `linear-gradient(90deg, #4A90D9 0%, #4A90D9 ${scorePercent}%, rgba(255,255,255,0.2) ${scorePercent}%)`
              }}
              onChange={e => setFilter('minScore', Number(e.target.value))}
            />
            <span className="range-val">10</span>
          </div>
        </div>

        <FilterGroup
          label="Домен"
          options={options.domains}
          selected={domains}
          onToggle={v => toggleMulti('domains', v)}
          onSetAll={vals => setMulti('domains', vals)}
          onClearAll={() => setMulti('domains', [])}
          capitalizeVal
        />
        <FilterGroup
          label="Категорія"
          options={options.categories.filter(([v]) => v !== 'Всі категорії')}
          selected={categories}
          onToggle={v => toggleMulti('categories', v)}
          onSetAll={vals => setMulti('categories', vals)}
          onClearAll={() => setMulti('categories', [])}
        />
        <FilterGroup
          label="Країна"
          options={options.countries}
          selected={countries}
          onToggle={v => toggleMulti('countries', v)}
          onSetAll={vals => setMulti('countries', vals)}
          onClearAll={() => setMulti('countries', [])}
        />
        <FilterGroup
          label="Сировина"
          options={options.commodities}
          selected={commodities}
          onToggle={v => toggleMulti('commodities', v)}
          onSetAll={vals => setMulti('commodities', vals)}
          onClearAll={() => setMulti('commodities', [])}
        />

      </div>
  );

  if (inDrawer) return inner;
  return <div className="sidebar">{inner}</div>;
}

function FilterGroup({ label, options, selected, onToggle, onSetAll, onClearAll, capitalizeVal }) {
  const [q, setQ] = useState('');
  if (!options || options.length === 0) return null;

  const visible = q.trim()
    ? options.filter(([val]) => val.toLowerCase().includes(q.toLowerCase()))
    : options;

  const visibleVals = visible.map(([val]) => val);
  const allVisibleSelected = visibleVals.length > 0 && visibleVals.every(v => selected.includes(v));
  const anyVisible = visibleVals.some(v => selected.includes(v));

  const selectAll = () => {
    if (onSetAll) {
      onSetAll(visibleVals);
    } else {
      visibleVals.forEach(val => {
        if (!selected.includes(val)) onToggle(val);
      });
    }
  };

  const clearAll = () => {
    if (onClearAll) {
      onClearAll();
    } else {
      selected.forEach(val => {
        if (visibleVals.includes(val)) onToggle(val);
      });
    }
  };

  return (
    <div className="filter-group">
      <div className="filter-label">{label}</div>
      {options.length > 5 && (
        <input
          className="filter-search"
          placeholder={`Пошук...`}
          value={q}
          onChange={e => setQ(e.target.value)}
        />
      )}
      {visibleVals.length > 0 && (
        <div className="filter-actions">
          <button className="filter-action-btn" onClick={selectAll}>
            {allVisibleSelected ? '✓' : '○'} Вибрати все
          </button>
          {anyVisible && (
            <button className="filter-action-btn" onClick={clearAll}>
              ✕ Зняти вибір
            </button>
          )}
        </div>
      )}
      <div className="chk-list">
        {visible.map(([val, cnt]) => (
          <label key={val} className="chk-item">
            <input
              type="checkbox"
              checked={selected.includes(val)}
              onChange={() => onToggle(val)}
            />
            {capitalizeVal ? capitalize(val) : val}
            <span className="chk-count">{cnt}</span>
          </label>
        ))}
        {visible.length === 0 && (
          <div className="filter-no-results">Не знайдено</div>
        )}
      </div>
    </div>
  );
}
