import { useState } from 'react';

export function Modal({ onSave }) {
  const [value, setValue] = useState('');

  const handle = (e) => {
    e.preventDefault();
    if (value.trim()) onSave(value.trim());
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Ласкаво просимо!</h2>
        <p>Введіть ваше ім'я або нікнейм для персоналізації системи.</p>
        <form onSubmit={handle}>
          <input
            autoFocus
            placeholder="Наприклад: Олена К."
            value={value}
            onChange={e => setValue(e.target.value)}
          />
          <button type="submit" className="modal-btn" disabled={!value.trim()}>
            Продовжити
          </button>
        </form>
      </div>
    </div>
  );
}
