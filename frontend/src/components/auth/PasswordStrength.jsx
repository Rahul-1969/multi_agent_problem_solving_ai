import React from 'react';
import { passwordStrength } from '../../utils/validation';

export default function PasswordStrength({ password }) {
  const { score, label } = passwordStrength(password);

  if (!password) return null;

  return (
    <div className="strength-meter-container">
      <div className="strength-bars">
        {[0, 1, 2, 3].map(idx => (
          <div 
            key={idx} 
            className={`strength-bar ${score >= idx ? `active-${score}` : ''}`} 
          />
        ))}
      </div>
      <div className="strength-text">Password Strength: {label}</div>
    </div>
  );
}
