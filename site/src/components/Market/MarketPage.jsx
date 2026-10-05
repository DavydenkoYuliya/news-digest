import { useState, useEffect } from 'react';
import { BriefCard } from './BriefCard';
import './market.css';

const SEL_KEY = 'mhp_market_sel';
const ONLY_KEY = 'mhp_market_only';

function load(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
}
function save(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}

// «Ринок закупівель»: ліворуч фільтр категорій і напрямів, праворуч довідки вибраних.
export function MarketPage({ market, newsByN, onRef, meta, focus }) {
  const withBrief = market.flatMap(g => g.entries).filter(e => e.brief).map(e => e.key);
  const [sel, setSel] = useState(() => load(SEL_KEY, null) || withBrief.slice(0, 3));
  const [only, setOnly] = useState(() => load(ONLY_KEY, true));
  const [q, setQ] = useState('');

  useEffect(() => { if (focus) setSel([focus.key]); }, [focus]);
  useEffect(() => { save(SEL_KEY, sel); }, [sel]);
  useEffect(() => { save(ONLY_KEY, only); }, [only]);

  const toggle = key => setSel(s => (s.includes(key) ? s.filter(k => k !== key) : [...s, key]));
  const all = market.flatMap(g => g.entries);
  const chosen = all.filter(e => sel.includes(e.key));

  if (!market.length) return <div className="market-page"><div className="empty-sel">Довідки ще не сформовано.</div></div>;

  return (
    <div className="market-page">
      <aside className="market-side">
        <input type="search" placeholder="Пошук…" value={q} onChange={e => setQ(e.target.value)} />
        <label className="ctl"><input type="checkbox" checked={only} onChange={e => setOnly(e.target.checked)} /> Тільки з публікаціями</label>
        <div className="ctl">
          <button className="btn" onClick={() => setSel(all.filter(e => !only || e.ids.length).map(e => e.key))}>Усі</button>
          <button className="btn" onClick={() => setSel([])}>Очистити</button>
          <button className="btn primary" onClick={() => window.print()}>Друк / PDF</button>
        </div>
        {market.map(g => (
          <div key={g.group}>
            <div className="grp">{g.group}</div>
            {g.entries
              .filter(e => (!only || e.ids.length > 0 || sel.includes(e.key)) && e.label.toLowerCase().includes(q.toLowerCase()))
              .map(e => (
                <div key={e.key} className={`row${sel.includes(e.key) ? ' sel' : ''}`} onClick={() => toggle(e.key)}>
                  <input type="checkbox" readOnly checked={sel.includes(e.key)} tabIndex={-1} />
                  <span className={`has${e.brief ? '' : ' off'}`} title={e.brief ? 'Є довідка' : 'Лише перелік публікацій'} />
                  <span className="lab">{e.label}</span>
                  <span className="cnt" title="Публікацій за період">{e.ids.length}</span>
                </div>
              ))}
          </div>
        ))}
        <div className="legend"><span className="has" /> є довідка · число — публікацій за період</div>
      </aside>
      <div className="market-body">
        <div className="market-intro">
          Щоночі AI готує коротку довідку по кожній категорії закупівель і напряму, де за період є щонайменше{' '}
          {meta.minNews || 5} публікацій: спершу висновок, далі факти з посиланнями на новини. Для категорій з меншою
          кількістю новин довідки немає — показано самі новини. Оберіть категорії ліворуч.
        </div>
        {chosen.length
          ? chosen.map(e => <BriefCard key={e.key} entry={e} newsByN={newsByN} onRef={onRef} meta={meta} />)
          : <div className="empty-sel">Оберіть категорії або напрями ліворуч.</div>}
      </div>
    </div>
  );
}
