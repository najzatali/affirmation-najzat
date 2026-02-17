"use client";

import Link from "next/link";
import { useMemo } from "react";

import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { i18n } from "../../lib/i18n";
import { readHistory } from "../../lib/studioStorage";

function formatDate(value, lang) {
  try {
    return new Date(value).toLocaleString(lang === "ru" ? "ru-RU" : "en-US");
  } catch (_e) {
    return value;
  }
}

export default function LibraryPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  const items = useMemo(() => readHistory(), []);

  return (
    <main className="page-shell">
      <AppNav title={t.library.title} subtitle={t.library.subtitle} />

      <section className="card">
        <div className="hero-actions" style={{ marginTop: 0 }}>
          <Link className="btn" href="/onboarding">
            {t.library.openOnboarding}
          </Link>
        </div>
      </section>

      <section className="card">
        {items.length === 0 ? (
          <p className="muted">{t.library.empty}</p>
        ) : (
          <ul className="history-list">
            {items.map((item) => (
              <li className="history-item" key={item.id}>
                <div className="row-between">
                  <strong>{formatDate(item.createdAt, lang)}</strong>
                  <span className={`status-pill ${item.status}`}>{item.status || "created"}</span>
                </div>

                <div className="history-meta">
                  <span>
                    {t.library.areas}: {(item.areas || []).join(", ") || "-"}
                  </span>
                  <span>
                    {t.library.duration}: {item.durationSec ? `${Math.floor(item.durationSec / 60)} ${t.common.minute}` : "-"}
                  </span>
                </div>

                {item.resultUrl ? (
                  <a className="btn-ghost" href={item.resultUrl} target="_blank" rel="noreferrer">
                    {t.library.openAudio}
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
