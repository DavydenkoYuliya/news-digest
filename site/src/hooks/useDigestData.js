import { useState, useEffect } from 'react';
import { getDomainKey, cleanSource } from '../utils/constants';

// Стабільний id новини (для закладок) — з посилання, а не з порядкового номера.
function hashId(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return 'u' + (h >>> 0).toString(36);
}

function toNews(it) {
  const d = it.date ? new Date(it.date) : null;
  const sourceRaw = String(it.source || '').trim();
  return {
    id: it.url ? hashId(it.url) : `n${it.n}`,
    n: it.n,
    section: it.section,
    company: it.company || '',
    date: d && !isNaN(d.getTime()) ? d : null,
    source: cleanSource(sourceRaw) || sourceRaw.slice(0, 30),
    title: it.title || '',
    summary: it.summary || '',
    detailed: it.detailed || '',
    domain: it.domain || '',
    domainKey: getDomainKey(it.domain || ''),
    category: it.category || '',
    country: it.country || '',
    commodity: it.commodity || '',
    url: it.url || '',
    score: Number(it.score) || 0,
  };
}

// Один файл data/digest.json: стрічка, «Ринок закупівель», «Головне сьогодні».
export function useDigestData() {
  const [state, setState] = useState({ news: [], market: [], today: null, meta: {}, loading: true, error: null });

  useEffect(() => {
    const base = process.env.PUBLIC_URL || '.';
    fetch(`${base}/data/digest.json?t=${Date.now()}`, { cache: 'no-store' })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(d => setState({
        news: (d.items || []).map(toNews).filter(n => n.title),
        market: d.market || [],
        today: d.today || null,
        meta: { generated: d.generated, period: d.period, model: d.model, promptVersion: d.prompt_version,
                domainLabels: d.domain_labels || {}, minNews: d.min_news || 5 },
        loading: false,
        error: null,
      }))
      .catch(e => setState(s => ({ ...s, loading: false, error: e.message })));
  }, []);

  return state;
}
