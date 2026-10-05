// Посилання [N] на новину зі стрічки: клік переносить у «Новини» і підсвічує картку.
export function Ref({ n, newsByN, onRef }) {
  const item = newsByN.get(n);
  return (
    <button className="ref-chip" title={item ? item.title : ''} onClick={() => onRef(n)}>[{n}]</button>
  );
}

export function Refs({ refs, newsByN, onRef }) {
  return (refs || []).map(n => <Ref key={n} n={n} newsByN={newsByN} onRef={onRef} />);
}
