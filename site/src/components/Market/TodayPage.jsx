import { Refs } from './Ref';

const CONF = { hi: ['c-hi', 'висока'], mid: ['c-mid', 'середня'], lo: ['c-lo', 'низька'] };

// «Головне сьогодні»: найважливіші події з довідок + головне з брифінгу конкурентів.
export function TodayPage({ today, meta, newsByN, onRef, openMarket, openCompetitors }) {
  if (!today) return <div className="market-page"><div className="empty-sel">Дані ще не сформовано.</div></div>;
  return (
    <div className="today-page">
      <h1>Головне сьогодні</h1>
      <p className="sub">Що треба знати за 2 хвилини{meta.period ? ` · ${meta.period}` : ''}</p>
      <div className="today-grid">
        <div>
          <h2>Закупівлі</h2>
          {today.proc.length === 0 && <p className="sub">Суттєвих подій не виявлено.</p>}
          {today.proc.map((x, i) => (
            <div key={i} className="tcard" onClick={() => openMarket(x.go)}>
              <div className="tt">{x.t}</div>
              <div className="tm">
                <span>{x.m}</span>
                {CONF[x.conf] && <span className={`conf ${CONF[x.conf][0]}`}>впевненість: {CONF[x.conf][1]}</span>}
                <span onClick={e => e.stopPropagation()}><Refs refs={x.refs.slice(0, 3)} newsByN={newsByN} onRef={onRef} /></span>
              </div>
              <div className="go">Відкрити довідку →</div>
            </div>
          ))}
        </div>
        <div>
          <h2>Конкуренти</h2>
          {(today.comp || []).length === 0 && <p className="sub">Суттєвих подій не виявлено.</p>}
          {(today.comp || []).map((t, i) => (
            <div key={i} className="tcard" onClick={openCompetitors}>
              <div className="tt">{t}</div>
              <div className="go">Відкрити брифінг конкурентів →</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
