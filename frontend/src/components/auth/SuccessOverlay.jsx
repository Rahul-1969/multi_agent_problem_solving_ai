import React from 'react';
import { Check } from 'lucide-react';

export default function SuccessOverlay({ show, message }) {
  if (!show) return null;

  return (
    <div className="success-overlay" aria-live="assertive">
      <div className="success-icon-wrapper">
        <Check size={40} strokeWidth={3} />
      </div>
      <div className="success-text">{message}</div>
    </div>
  );
}
