"use client";

import { useEffect, useState } from "react";

import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { apiGet, apiPost } from "../../lib/api";
import { i18n } from "../../lib/i18n";

export default function BillingPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  const [packages, setPackages] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [busyDuration, setBusyDuration] = useState(0);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function load() {
    try {
      const [pkg, pur] = await Promise.all([apiGet("/api/billing/packages"), apiGet("/api/billing/purchases")]);
      setPackages(Array.isArray(pkg) ? pkg : []);
      setPurchases(Array.isArray(pur) ? pur : []);
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function activate(durationSec) {
    setBusyDuration(durationSec);
    setError("");
    setSuccess("");

    try {
      await apiPost("/api/billing/purchases", {
        duration_sec: durationSec,
        success_url: `${window.location.origin}/billing/success`,
        cancel_url: `${window.location.origin}/billing/cancel`,
      });
      setSuccess(lang === "ru" ? "Покупка добавлена" : "Purchase added");
      await load();
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    } finally {
      setBusyDuration(0);
    }
  }

  return (
    <main className="page-shell">
      <AppNav title={t.billing.title} subtitle={t.billing.subtitle} />

      <section className="card">
        <h2>{t.billing.packages}</h2>
        <div className="grid grid-3">
          {packages.map((item) => (
            <article key={item.code} className="price-card">
              <strong>{item.duration_label}</strong>
              <p className="muted">{item.price_rub === 0 ? t.common.demo : `${item.price_rub} ₽`}</p>
              <button
                type="button"
                className={item.is_demo ? "btn-ghost" : "btn"}
                disabled={busyDuration === item.duration_sec}
                onClick={() => activate(item.duration_sec)}
              >
                {busyDuration === item.duration_sec ? t.common.loading : t.billing.activate}
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>{t.billing.activePurchases}</h2>
        {purchases.length === 0 ? (
          <p className="muted">{t.common.noData}</p>
        ) : (
          <ul className="history-list">
            {purchases.map((item) => (
              <li key={item.id} className="history-item">
                <div className="row-between">
                  <strong>{item.duration_sec === 30 ? "30 sec" : `${Math.floor(item.duration_sec / 60)} min`}</strong>
                  <span className={`status-pill ${item.status}`}>{item.status}</span>
                </div>
                <div className="history-meta">
                  <span>{item.price_rub} ₽</span>
                  <span>
                    {t.billing.status}: {item.consumed ? t.billing.consumed : t.billing.notConsumed}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <p className="footnote">{t.billing.note}</p>
      </section>

      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}
    </main>
  );
}
