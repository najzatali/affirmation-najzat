"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import AppNav from "../components/AppNav";
import { useLanguage } from "../components/LanguageContext";
import { i18n } from "../lib/i18n";
import { formatRub } from "../lib/pricing";

export default function HomePage() {
  const { lang } = useLanguage();
  const t = i18n[lang];
  const locale = lang === "ru" ? "ru-RU" : "en-US";

  const [employees, setEmployees] = useState(10);
  const [hoursSaved, setHoursSaved] = useState(2);
  const [hourRate, setHourRate] = useState(900);

  const monthlySaving = useMemo(() => {
    const staff = Math.max(1, Number(employees || 0));
    const hours = Math.max(0, Number(hoursSaved || 0));
    const rate = Math.max(0, Number(hourRate || 0));
    return Math.round(staff * hours * rate * 4);
  }, [employees, hoursSaved, hourRate]);

  return (
    <main className="page-shell">
      <AppNav title={t.home.title} subtitle={t.home.subtitle} />

      <section className="card hero glow">
        <p className="badge">{t.home.badge}</p>
        <div className="hero-actions">
          <Link className="btn" href="/onboarding">
            {t.home.ctaPrimary}
          </Link>
          <Link className="btn btn-ghost" href="/billing">
            {t.home.ctaSecondary}
          </Link>
        </div>

        <div className="stats-strip">
          {t.home.trustStats.map((item) => (
            <article key={item.label} className="stat-chip">
              <strong>{item.value}</strong>
              <p className="muted">{item.label}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.home.highlightsTitle}</h2>
        <div className="grid grid-3">
          {t.home.highlights.map((item) => (
            <article key={item.title} className="feature-card">
              <h3>{item.title}</h3>
              <p className="muted">{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.home.evidenceTitle}</h2>
        <p className="muted">{t.home.evidenceHint}</p>
        <div className="grid grid-2">
          {t.home.evidence.map((item) => (
            <article key={item.title} className="feature-card">
              <h3>{item.title}</h3>
              <p className="muted">{item.text}</p>
              <a className="link-btn" href={item.href} target="_blank" rel="noreferrer">
                {t.home.openSource}
              </a>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.home.tracksTitle}</h2>
        <div className="grid grid-4">
          {t.home.tracks.map((item) => (
            <article key={item.title} className="track-card">
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.home.flowTitle}</h2>
        <div className="timeline-grid">
          {t.home.flow.map((step) => (
            <article className="timeline-item" key={step.title}>
              <h3>{step.title}</h3>
              <p className="muted">{step.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="card glow roi-block">
        <h2>{t.home.roiTitle}</h2>
        <p className="muted">{t.home.roiHint}</p>
        <div className="roi-grid">
          <div>
            <label>{t.home.roiEmployees}</label>
            <input
              className="input"
              type="number"
              min={1}
              max={100}
              value={employees}
              onChange={(event) => setEmployees(Number(event.target.value || 1))}
            />
          </div>
          <div>
            <label>{t.home.roiHours}</label>
            <input
              className="input"
              type="number"
              min={0}
              max={20}
              step={0.5}
              value={hoursSaved}
              onChange={(event) => setHoursSaved(Number(event.target.value || 0))}
            />
          </div>
          <div>
            <label>{t.home.roiRate}</label>
            <input
              className="input"
              type="number"
              min={0}
              step={50}
              value={hourRate}
              onChange={(event) => setHourRate(Number(event.target.value || 0))}
            />
          </div>
        </div>
        <div className="roi-result">
          <p className="muted">{t.home.roiResult}</p>
          <strong>{formatRub(monthlySaving, locale)}</strong>
        </div>
      </section>
    </main>
  );
}
