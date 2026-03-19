import { capitalize } from '../../utils/constants';

export function Sidebar({ filters, options, setFilter, toggleMulti, reset, totalCount, inDrawer }) {
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
          capitalizeVal
        />
        <FilterGroup
          label="Категорія"
          options={options.categories.filter(([v]) => v !== 'Всі категорії')}
          selected={categories}
          onToggle={v => toggleMulti('categories', v)}
        />
        <FilterGroup
          label="Країна"
          options={options.countries}
          selected={countries}
          onToggle={v => toggleMulti('countries', v)}
        />
        <FilterGroup
          label="Сировина"
          options={options.commodities}
          selected={commodities}
          onToggle={v => toggleMulti('commodities', v)}
        />

        <div className="found-count">Знайдено: {totalCount} новин</div>
        <button className="reset-btn" onClick={reset}>Скинути всі фільтри</button>
      </div>
  );

  if (inDrawer) return inner;
  return <div className="sidebar">{inner}</div>;
}

function FilterGroup({ label, options, selected, onToggle, capitalizeVal }) {
  if (!options || options.length === 0) return null;
  return (
    <div className="filter-group">
      <div className="filter-label">{label}</div>
      <div className="chk-list">
        {options.map(([val, cnt]) => (
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
      </div>
    </div>
  );
}
