import { render, screen } from '@testing-library/react';
import { BriefCard } from './components/Market/BriefCard';

const news = new Map([[7, { n: 7, title: 'Премія на аргентинський шрот', url: 'https://x', source: 'UkrAgroConsult', date: new Date('2026-10-01') }]]);

test('довідка: спершу висновок, потім факти з посиланнями', () => {
  const entry = {
    key: 'cat:X', label: 'Незернові компоненти', ids: [7],
    brief: {
      verdict: 'Ціни на соєвий шрот зростають', why: ['Може позначитися на пропозиціях'],
      facts: [{ text: 'Премія на максимумі з травня', refs: [7] }],
      events: [{ text: 'Премія зросла', refs: [7], type: 'Ціни', confidence: 'mid', key: true }],
      related: [], badge: { text: 'Ціновий тиск', tone: 'warn' }, no_news: false, profile: [],
    },
  };
  render(<BriefCard entry={entry} newsByN={news} onRef={() => {}} meta={{}} />);
  expect(screen.getByText('Ціни на соєвий шрот зростають')).toBeInTheDocument();
  expect(screen.getByText(/Премія на максимумі з травня/)).toBeInTheDocument();
  expect(screen.getAllByText('[7]').length).toBeGreaterThan(0);
});
