import React from 'react';

export default function LoadingButton({ loading, disabled, children, ...props }) {
  return (
    <button 
      className="auth-submit-btn" 
      disabled={loading || disabled}
      aria-disabled={loading || disabled}
      {...props}
    >
      {loading ? (
        <span className="auth-spinner" aria-label="Loading" />
      ) : (
        children
      )}
    </button>
  );
}
