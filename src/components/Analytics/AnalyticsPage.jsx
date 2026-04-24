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
  const [domain, setDomain] = useState('');
  const [category, setCategory] = useState('');
  const [commodity, setCommodity] = useState('');
  const [country, setCountry] = useState('');
  const { generate, result, loading, error, clear } = useAnalyticsGeneration();

  const filters = { domains: domain ? [domain] : [], categories: category ? [category] : [], commodities: commodity ? [commodity] : [], countries: country ? [country] : [] };

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

  const hasFilters = domain || category || commodity || country;
  const filterLabel = [domain, category, commodity, country].filter(Boolean).join(', ') || 'всі новини';
  const newsCount = filtered.length;
  const usedCount = Math.min(newsCount, 30);

  const handleChange = (setter) => (e) => { setter(e.target.value); clear(); };
  const handleReset = () => { setDomain(''); setCategory(''); setCommodity(''); setCountry(''); clear(); };

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
        <div className="analytics-filter-bar">
          <select className="analytics-select" value={domain} onChange={handleChange(setDomain)}>
            <option value="">Всі домени</option>
            {options.domains.map(([d]) => <option key={d} value={d}>{d}</option>)}
          </select>
          <select className="analytics-select" value={category} onChange={handleChange(setCategory)}>
            <option value="">Всі категорії</option>
            {options.categories.map(([c]) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="analytics-select" value={commodity} onChange={handleChange(setCommodity)}>
            <option value="">Вся сировина</option>
            {options.commodities.map(([c]) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select className="analytics-select" value={country} onChange={handleChange(setCountry)}>
            <option value="">Всі країни</option>
            {options.countries.map(([c]) => <option key={c} value={c}>{c}</option>)}
          </select>
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
