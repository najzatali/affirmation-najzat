"use client";

export default function BrandLogo({ className = "" }) {
  return (
    <div className={`brand-logo ${className}`.trim()} aria-label="Affirmation Studio logo">
      <svg viewBox="0 0 56 56" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="affirmGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#f97316" />
            <stop offset="55%" stopColor="#fb7185" />
            <stop offset="100%" stopColor="#38bdf8" />
          </linearGradient>
        </defs>
        <rect x="3" y="3" width="50" height="50" rx="16" fill="url(#affirmGrad)" />
        <path d="M17 30c5-2 8-7 11-12 3 5 6 10 11 12-5 2-8 7-11 12-3-5-6-10-11-12z" fill="#fff7ed" />
      </svg>
      <div>
        <strong>Affirmation</strong>
        <p>Studio</p>
      </div>
    </div>
  );
}
