import React from 'react';
import { Check } from 'lucide-react';

export default function AuthInput({ 
  id, 
  label, 
  icon: Icon, 
  type = "text", 
  valid = null, 
  error = "",
  rightElement = null,
  disabled = false,
  ...props 
}) {
  let wrapClass = "auth-input-wrap";
  if (valid === true) wrapClass += " valid";
  if (valid === false) wrapClass += " invalid";

  return (
    <div className="auth-field">
      <label className="auth-label" htmlFor={id}>{label}</label>
      <div className={wrapClass}>
        {Icon && <Icon className="auth-icon" size={18} />}
        <input
          id={id}
          type={type}
          className="auth-input"
          disabled={disabled}
          aria-invalid={valid === false}
          {...props}
        />
        {valid === true && <Check className="auth-check" size={20} />}
        {rightElement}
      </div>
      {error && valid === false && (
        <div className="auth-inline-error" aria-live="polite">{error}</div>
      )}
    </div>
  );
}
