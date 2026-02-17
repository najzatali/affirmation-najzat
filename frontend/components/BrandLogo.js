"use client";

export default function BrandLogo({ className = "" }) {
  return (
    <div className={`brand-logo ${className}`.trim()} aria-label="AIMPACT Academy logo">
      <svg viewBox="0 0 56 56" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="logoGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#00b6ff" />
            <stop offset="55%" stopColor="#00d399" />
            <stop offset="100%" stopColor="#ff7a2f" />
          </linearGradient>
        </defs>
        <rect x="3" y="3" width="50" height="50" rx="15" fill="url(#logoGrad)" />
        <path
          d="M16 33 L28 14 L40 33 L31 30 L28 43 L25 30 Z"
          fill="#fff8ef"
          opacity="0.96"
        />
        <circle cx="28" cy="28" r="4" fill="#0d2f4f" opacity="0.85" />
      </svg>
      <div>
        <strong>AIMPACT</strong>
        <p>Academy</p>
      </div>
    </div>
  );
}
