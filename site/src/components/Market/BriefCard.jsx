import { Refs } from './Ref';
import { formatDateShort } from '../../utils/dateUtils';

const CONF = { hi: ['c-hi', 'висока'], mid: ['c-mid', 'середня'], lo: ['c-lo', 'низька'] };

export function plural(n, forms) {
  const a = n % 10, b = n % 100;
  const w = a === 1 && b !== 11 ? forms[0] : a >= 2 && a <= 4 && (b < 12 || b > 14) ? forms[1] : forms[2];
  return `${n} ${w}`;
}
const pub = n => plural(n, ['публікація', 'публікації', 'публікацій']);

function EventsTable({ rows, newsByN, onRef }) {
  return (
    <table className="brief-table">
      <thead><tr><th>Дата</th><th>Подія</th><th>Джерело</th><th>Тип</th><th>Впевненість</th></tr></thead>
      <tbody>
        {rows.map((e, i) => {
          const first = newsByN.get(e.refs[0]) || {};
          const c = CONF[e.confidence];
          return (
            <tr key={i} className={e.key ? 'key' : ''}>
              <td className="date">{first.date ? formatDateShort(first.date) : ''}</td>
              <td>
                <span className="dot" />
                {first.url ? <a href={first.url} target="_blank" rel="noopener noreferrer">{e.text}</a> : e.text}
                {e.refs.length > 1 && <span className="muted"> · {pub(e.refs.length)}</span>}{' '}
                <Refs refs={e.refs} newsByN={newsByN} onRef={onRef} />
              </td>
              <td>{first.source || ''}</td>
              <td><span className="cat">{e.type || '—'}</span></td>
              <td>{c ? <span className={`conf ${c[0]}`}>{c[1]}</span> : <span className="muted">—</span>}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

// Перелік публікацій без довідки: дата, новина, джерело, напрям (людською назвою).
function NewsList({ ids, newsByN, onRef, domainLabels }) {
  return (
    <table className="brief-table">
      <thead><tr><th>Дата</th><th>Новина</th><th>Джерело</th><th>Напрям</th></tr></thead>
      <tbody>
        {ids.map(n => {
          const it = newsByN.get(n) || {};
          return (
            <tr key={n}>
              <td className="date">{it.date ? formatDateShort(it.date) : ''}</td>
              <td>
                {it.url ? <a href={it.url} target="_blank" rel="noopener noreferrer">{it.title}</a> : it.title}{' '}
                <Refs refs={[n]} newsByN={newsByN} onRef={onRef} />
                {it.detailed && it.detailed !== it.title && <div className="news-explain">{it.detailed}</div>}
              </td>
              <td>{it.source || ''}</td>
              <td><span className="cat">{(domainLabels && domainLabels[it.domain]) || it.domain || '—'}</span></td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

// Картка довідки: висновок (загальний → конкретний) → ключові факти → згорнуті «Джерела і деталі».
export function BriefCard({ entry, newsByN, onRef, meta }) {
  const b = entry.brief;
  const count = entry.ids.length;
  const minNews = meta.minNews || 5;

  if (!b) {
    const few = count < minNews;
    return (
      <div className="brief-card">
        <div className="brief-head">
          {entry.label}
          {count > 0 && few && <span className="badge t-none">Мало даних</span>}
          <span className="n">{pub(count)}</span>
        </div>
        {count === 0
          ? <p className="none">За період у цій категорії публікацій немає.</p>
          : <>
              <div className="explain">
                {few
                  ? <>За період у цій категорії лише {pub(count)} — замало, щоб робити висновки (довідка
                      створюється, коли публікацій щонайменше {minNews}). Нижче — самі новини з коротким поясненням
                      кожної: назва відкриває статтю, номер [N] показує новину в стрічці.</>
                  : <>Довідку для цієї групи не сформовано. Нижче — новини за період з коротким поясненням кожної:
                      назва відкриває статтю, номер [N] показує новину в стрічці.</>}
              </div>
              <NewsList ids={entry.ids} newsByN={newsByN} onRef={onRef} domainLabels={meta.domainLabels} />
            </>}
      </div>
    );
  }

  const tone = (b.badge && b.badge.tone) || 'neutral';
  const nEv = (b.events || []).length;
  const hasDetails = nEv || (b.related || []).length || (b.profile || []).length;

  return (
    <div className="brief-card">
      <div className="brief-head">
        {entry.label}
        {b.badge && b.badge.text && <span className={`badge t-${tone}`}>{b.badge.text}</span>}
        <span className="n">{pub(count)}</span>
      </div>

      {b.no_news
        ? <p className="none">Без суттєвих подій за період.</p>
        : <>
            {b.verdict && <>
              <div className="sec">Висновок <i>(не факт)</i></div>
              <div className="verdict">{b.verdict}</div>
              {(b.why || []).length > 0 && <ul className="note">{b.why.map((w, i) => <li key={i}>{w}</li>)}</ul>}
            </>}
            {(b.facts || []).length > 0 && <>
              <div className="sec">Ключові факти</div>
              <ul className="bullets">
                {b.facts.map((f, i) => <li key={i}>{f.text} <Refs refs={f.refs} newsByN={newsByN} onRef={onRef} /></li>)}
              </ul>
            </>}
          </>}

      {hasDetails ? (
        <details className="dd">
          <summary>Джерела і деталі{nEv ? ` · ${plural(nEv, ['подія', 'події', 'подій'])}` : ''} · {pub(count)}</summary>
          {nEv > 0 && <><div className="sec">Події</div><EventsTable rows={b.events} newsByN={newsByN} onRef={onRef} /></>}
          {(b.related || []).length > 0 && <>
            <div className="sec">Пов'язані сигнали з інших напрямів</div>
            <ul className="note">{b.related.map((r, i) => <li key={i}>{r.text} <Refs refs={[r.ref]} newsByN={newsByN} onRef={onRef} /></li>)}</ul>
          </>}
          {(b.profile || []).length > 0 && <>
            <div className="sec">Профіль категорії</div>
            <div className="profile">{b.profile.map(([k, v]) => [<div key={k} className="pl">{k}</div>, <div key={k + 'v'} className="pv">{v}</div>])}</div>
          </>}
        </details>
      ) : null}

      <div className="meta-foot">Згенеровано AI · {b.model || meta.model} · версія інструкції {b.prompt_version || meta.promptVersion}</div>
    </div>
  );
}
