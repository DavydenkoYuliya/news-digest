import { useState, useMemo } from 'react';
import { useAnalyticsGeneration } from '../../hooks/useAnalyticsGeneration';

function applyFilters(news, filters, skip = []) {
  let result = news;

  if (!skip.includes('domains') && filters.domains.length > 0) {
    result = result.filter(n => filters.domains.includes(n.domain));
  }
  if (!skip.includes('categories') && filters.categories.length > 0) {
    result = result.filter(n => filters.categories.some(c => n.category.includes(c)));
  }
  if (!skip.includes('countries') && filters.countries.length > 0) {
    result = result.filter(n => {
      const parts = n.country.split(',').map(s => s.trim());
      return filters.countries.some(c => parts.includes(c));
    });
  }
  if (!skip.includes('commodities') && filters.commodities.length > 0) {
    result = result.filter(n => {
      const parts = n.commodity.split(',').map(s => s.trim());
      return filters.commodities.some(c => parts.includes(c));
    });
  }

  return result;
}

function countField(rows, key) {
  const map = {};
  rows.forEach(n => {
    const val = n[key];
    if (!val) return;
    const parts = String(val).split(',').map(s => s.trim()).filter(Boolean);
    parts.forEach(p => { map[p] = (map[p] || 0) + 1; });
  });
  return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0], 'uk-UA', { sensitivity: 'base' }));
}

function AnalyticsFilterGroup({ label, options, selected, onToggle, onSetAll, onClearAll, expanded, onExpand }) {
  const [q, setQ] = useState('');
  if (!options || options.length === 0) return null;

  const visible = q.trim()
    ? options.filter(([val]) => val.toLowerCase().includes(q.toLowerCase()))
    : options;

  const selectedCount = selected.length;
  const visibleVals = visible.map(([val]) => val);
  const allVisibleSelected = visibleVals.length > 0 && visibleVals.every(v => selected.includes(v));
  const anyVisible = visibleVals.some(v => selected.includes(v));

  const getBadgeText = () => {
    if (selectedCount === 0) return null;
    if (selectedCount === 1) return selected[0];
    return `Вибрано ${selectedCount}`;
  };

  const selectAll = () => {
    if (onSetAll) {
      onSetAll(visibleVals);
    }
  };

  const clearAll = () => {
    if (onClearAll) {
      onClearAll();
    }
  };

  return (
    <div className="analytics-filter-group">
      <button
        className="analytics-filter-button"
        onClick={onExpand}
      >
        <span className="analytics-filter-label">{label}</span>
        {selectedCount > 0 && <span className="analytics-filter-badge">{getBadgeText()}</span>}
        <span className="analytics-filter-arrow">{expanded ? '▼' : '▶'}</span>
      </button>
      {expanded && (
        <div className="analytics-filter-dropdown">
          {options.length > 5 && (
            <input
              className="analytics-filter-search"
              placeholder="Пошук..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          )}
          {visibleVals.length > 0 && (
            <div className="analytics-filter-actions">
              <button className="analytics-filter-action-btn" onClick={selectAll}>
                {allVisibleSelected ? '✓' : '○'} Вибрати все
              </button>
              {anyVisible && (
                <button className="analytics-filter-action-btn" onClick={clearAll}>
                  ✕ Зняти вибір
                </button>
              )}
            </div>
          )}
          <div className="analytics-chk-list">
            {visible.map(([val, cnt]) => (
              <label key={val} className="analytics-chk-item">
                <input
                  type="checkbox"
                  checked={selected.includes(val)}
                  onChange={() => onToggle(val)}
                />
                {val}
                <span className="analytics-chk-count">{cnt}</span>
              </label>
            ))}
            {visible.length === 0 && (
              <div className="analytics-filter-no-results">Не знайдено</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function AnalyticsResult({ text }) {
  return (
    <div className="ar-body">
      {text.split('\n').map((line, i) => {
        if (!line.trim()) return <div key={i} className="ar-gap" />;

        const renderInline = (str) => {
          const parts = str.split(/(\*\*[^*]+\*\*)/g);
          return parts.map((part, j) =>
            part.startsWith('**') && part.endsWith('**')
              ? <strong key={j}>{part.slice(2, -2)}</strong>
              : part
          );
        };

        if (/^\*\*\d+\./.test(line) || (line.startsWith('**') && line.endsWith('**'))) {
          return <div key={i} className="ar-heading">{renderInline(line)}</div>;
        }
        if (line.startsWith('- ') || line.startsWith('• ')) {
          return <div key={i} className="ar-bullet">{renderInline(line.slice(2))}</div>;
        }
        return <div key={i} className="ar-para">{renderInline(line)}</div>;
      })}
    </div>
  );
}

export function AnalyticsPage({ news }) {
  const [domains, setDomains] = useState([]);
  const [categories, setCategories] = useState([]);
  const [commodities, setCommodities] = useState([]);
  const [countries, setCountries] = useState([]);
  const [expandedFilter, setExpandedFilter] = useState(null);
  const { generate, result, loading, error, clear } = useAnalyticsGeneration();

  const filters = useMemo(() => ({ domains, categories, commodities, countries }), [domains, categories, commodities, countries]);

  const options = useMemo(() => {
    const domainList = countField(applyFilters(news, filters, ['domains']),     'domain');
    const categoryList = countField(applyFilters(news, filters, ['categories']),  'category');
    const commodityList = countField(applyFilters(news, filters, ['commodities']), 'commodity');
    const countryList = countField(applyFilters(news, filters, ['countries']),   'country');
    return { domains: domainList, categories: categoryList, commodities: commodityList, countries: countryList };
  }, [news, filters]);

  const filtered = useMemo(() => {
    return applyFilters(news, filters);
  }, [news, filters]);

  const hasFilters = domains.length > 0 || categories.length > 0 || commodities.length > 0 || countries.length > 0;
  const filterLabel = [...domains, ...categories, ...commodities, ...countries].join(', ') || 'всі новини';
  const newsCount = filtered.length;
  const usedCount = Math.min(newsCount, 30);

  const toggleFilter = (setter, arr, val) => {
    setter(arr.includes(val) ? arr.filter(v => v !== val) : [...arr, val]);
    clear();
  };

  const handleReset = () => {
    setDomains([]);
    setCategories([]);
    setCommodities([]);
    setCountries([]);
    setExpandedFilter(null);
    clear();
  };

  return (
    <div className="content">
      <div className="section-bar">
        <div className="section-title">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#4A90D9" strokeWidth="2">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          AI-Аналітика
        </div>
      </div>

      <div className="analytics-scroll">
        <div className="analytics-filters">
          <AnalyticsFilterGroup
            label="Домен"
            options={options.domains}
            selected={domains}
            onToggle={(v) => toggleFilter(setDomains, domains, v)}
            onSetAll={(vals) => setDomains(vals)}
            onClearAll={() => setDomains([])}
            expanded={expandedFilter === 'domains'}
            onExpand={() => setExpandedFilter(expandedFilter === 'domains' ? null : 'domains')}
          />
          <AnalyticsFilterGroup
            label="Категорія"
            options={options.categories}
            selected={categories}
            onToggle={(v) => toggleFilter(setCategories, categories, v)}
            onSetAll={(vals) => setCategories(vals)}
            onClearAll={() => setCategories([])}
            expanded={expandedFilter === 'categories'}
            onExpand={() => setExpandedFilter(expandedFilter === 'categories' ? null : 'categories')}
          />
          <AnalyticsFilterGroup
            label="Сировина"
            options={options.commodities}
            selected={commodities}
            onToggle={(v) => toggleFilter(setCommodities, commodities, v)}
            onSetAll={(vals) => setCommodities(vals)}
            onClearAll={() => setCommodities([])}
            expanded={expandedFilter === 'commodities'}
            onExpand={() => setExpandedFilter(expandedFilter === 'commodities' ? null : 'commodities')}
          />
          <AnalyticsFilterGroup
            label="Країна"
            options={options.countries}
            selected={countries}
            onToggle={(v) => toggleFilter(setCountries, countries, v)}
            onSetAll={(vals) => setCountries(vals)}
            onClearAll={() => setCountries([])}
            expanded={expandedFilter === 'countries'}
            onExpand={() => setExpandedFilter(expandedFilter === 'countries' ? null : 'countries')}
          />
          {hasFilters && (
            <button className="reset-btn analytics-reset-btn" onClick={handleReset}>Скинути</button>
          )}
        </div>

        <div className="analytics-action-bar">
          <span className="found-count">
            Знайдено: {newsCount} новин{newsCount > 30 ? ` · буде використано топ-${usedCount}` : ''}
          </span>
          <button
            className="analytics-gen-btn"
            onClick={() => generate(filtered, filterLabel)}
            disabled={loading || newsCount === 0}
          >
            {loading ? (
              <><span className="analytics-spinner" /> Аналізую...</>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
                Генерувати аналітику
              </>
            )}
          </button>
        </div>

        {error && <div className="analytics-error">{error}</div>}

        {result && (
          <div className="analytics-result-card">
            <div className="analytics-result-meta">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4A90D9" strokeWidth="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              Аналіз по: <strong>{filterLabel}</strong>
              <span className="analytics-result-count">· {usedCount} новин</span>
            </div>
            <AnalyticsResult text={result} />
          </div>
        )}

        {!result && !loading && !error && (
          <div className="analytics-placeholder">
            <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="rgba(74,144,217,0.25)" strokeWidth="1.2">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
            <span>Оберіть фільтри і натисніть «Генерувати аналітику»</span>
            <span className="analytics-placeholder-sub">AI проаналізує відфільтровані новини і надасть висновки щодо ризиків, можливостей та прогнозу</span>
          </div>
        )}
      </div>
    </div>
  );
}
