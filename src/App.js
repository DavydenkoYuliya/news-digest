import { useState } from 'react';
import * as XLSX from 'xlsx';
import './App.css';

import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Sidebar/Sidebar';
import { NewsFeed } from './components/NewsFeed/NewsFeed';
import { BookmarksPage } from './components/Bookmarks/BookmarksPage';
import { Toast, showToast } from './components/UI/Toast';
import { Modal } from './components/UI/Modal';

import { useExcelData } from './hooks/useExcelData';
import { useBookmarks } from './hooks/useBookmarks';
import { useFilters } from './hooks/useFilters';
import { useUser } from './hooks/useUser';

function App() {
  const [activeTab, setActiveTab] = useState('news');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { news, loading, loadFromFile } = useExcelData();
  const { bookmarkList, isBookmarked, toggle } = useBookmarks();
  const { filters, filtered, options, setFilter, toggleMulti, reset } = useFilters(news);
  const { name, initials, showModal, setShowModal, saveName } = useUser();

  const handleExport = () => {
    const rows = filtered.map(n => ({
      'Score':      n.score,
      'Дата':       n.date ? n.date.toLocaleString('uk-UA') : '',
      'Джерело':    n.source,
      'Заголовок':  n.title,
      'AI-резюме':  n.summary,
      'Домен':      n.domain,
      'Категорія':  n.category,
      'Країна':     n.country,
      'Сировина':   n.commodity,
      'Посилання':  n.url,
    }));
    const ws = XLSX.utils.json_to_sheet(rows);
    // Column widths
    ws['!cols'] = [8, 18, 16, 60, 80, 14, 16, 24, 20, 50].map(w => ({ wch: w }));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Новини');
    const date = new Date().toISOString().slice(0, 10);
    XLSX.writeFile(wb, `MHP_News_${date}.xlsx`);
    showToast(`Експортовано ${rows.length} новин`);
  };

  const handleToggleSave = (item) => {
    const wasAdded = toggle(item);
    showToast(wasAdded ? 'Новину збережено в закладки' : 'Новину видалено з закладок');
  };

  const activeFiltersCount = [
    filters.search ? 1 : 0,
    filters.minScore > 1 ? 1 : 0,
    filters.domains.length,
    filters.categories.length,
    filters.countries.length,
    filters.commodities.length,
  ].reduce((a, b) => a + b, 0);

  const userProps = { name, initials, openModal: () => setShowModal(true) };

  const sidebarProps = { filters, options, setFilter, toggleMulti, reset, totalCount: filtered.length };

  return (
    <div className="app">
      {showModal && <Modal onSave={saveName} />}

      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        bookmarkCount={bookmarkList.length}
        user={userProps}
        onExport={handleExport}
        onFilterToggle={() => setDrawerOpen(o => !o)}
        activeFiltersCount={activeFiltersCount}
      />

      {/* Mobile filter drawer */}
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
        {activeTab === 'news' && <Sidebar {...sidebarProps} />}

        {activeTab === 'news' ? (
          <div className="content">
            <NewsFeed
              news={filtered}
              loading={loading}
              filters={filters}
              setFilter={setFilter}
              isBookmarked={isBookmarked}
              onToggleSave={handleToggleSave}
            />
          </div>
        ) : (
          <BookmarksPage
            bookmarkList={bookmarkList}
            isBookmarked={isBookmarked}
            onToggleSave={handleToggleSave}
          />
        )}
      </div>

      <Toast />
    </div>
  );
}

export default App;
