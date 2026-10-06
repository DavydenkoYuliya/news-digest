import { useState, useMemo, useEffect } from 'react';
import './App.css';

import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Sidebar/Sidebar';
import { NewsFeed } from './components/NewsFeed/NewsFeed';
import { TodayPage } from './components/Market/TodayPage';
import { MarketPage } from './components/Market/MarketPage';
import { CompetitorsPage } from './components/Market/CompetitorsPage';

import { useDigestData } from './hooks/useDigestData';
import { useFilters } from './hooks/useFilters';

function App() {
  const [activeTab, setActiveTab] = useState('today');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [highlight, setHighlight] = useState(null);     // номер новини, на яку перейшли з довідки
  const [marketFocus, setMarketFocus] = useState(null); // категорія, відкрита з «Головне сьогодні»
  const { news, market, today, meta, loading } = useDigestData();
  const { filters, filtered, options, setFilter, toggleMulti, setMulti, reset } = useFilters(news);

  const newsByN = useMemo(() => new Map(news.map(n => [n.n, n])), [news]);

  useEffect(() => {
    if (highlight == null) return undefined;
    const t = setTimeout(() => setHighlight(null), 2500);
    return () => clearTimeout(t);
  }, [highlight]);

  // Посилання [N] у довідках → стрічка новин з підсвіченою карткою (фільтри скидаються, щоб її було видно)
  const openRef = (n) => {
    reset();
    setActiveTab('news');
    setHighlight(n);
  };
  const openMarket = (key) => { setMarketFocus({ key, t: Date.now() }); setActiveTab('market'); };

  const activeFiltersCount = [
    filters.search ? 1 : 0,
    filters.minScore > 1 ? 1 : 0,
    filters.domains.length,
    filters.categories.length,
    filters.countries.length,
    filters.commodities.length,
  ].reduce((a, b) => a + b, 0);

  const sidebarProps = { filters, options, setFilter, toggleMulti, setMulti, reset, totalCount: filtered.length,
                         domainLabels: meta.domainLabels || {} };

  return (
    <div className="app">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onFilterToggle={() => setDrawerOpen(o => !o)}
        activeFiltersCount={activeFiltersCount}
      />

      {drawerOpen && (
        <div className="drawer-overlay" onClick={() => setDrawerOpen(false)}>
          <div className="drawer" onClick={e => e.stopPropagation()}>
            <div className="drawer-header">
              <span>Фільтри</span>
              <button className="drawer-close" onClick={() => setDrawerOpen(false)}>✕</button>
            </div>
            <Sidebar {...sidebarProps} inDrawer />
          </div>
        </div>
      )}

      <div className="main">
        {activeTab === 'today' && !loading && (
          <TodayPage today={today} meta={meta} newsByN={newsByN} onRef={openRef}
                     openMarket={openMarket} openCompetitors={() => setActiveTab('competitors')} />
        )}

        {activeTab === 'news' && <Sidebar {...sidebarProps} />}
        {activeTab === 'news' && (
          <div className="content">
            <NewsFeed
              news={filtered}
              loading={loading}
              filters={filters}
              setFilter={setFilter}
              highlight={highlight}
            />
          </div>
        )}

        {activeTab === 'market' && !loading && (
          <MarketPage market={market} newsByN={newsByN} onRef={openRef} meta={meta} focus={marketFocus} />
        )}

        {activeTab === 'competitors' && <CompetitorsPage />}

      </div>

    </div>
  );
}

export default App;
