"use client";

import { useEffect, useMemo, useState } from "react";
import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { i18n } from "../../lib/i18n";
import { corporateTiers, formatRub, getTierForSeats } from "../../lib/pricing";

const API = process.env.NEXT_PUBLIC_API_URL;
const INDIVIDUAL_PRICE = 2990;

function statusLabel(status, lang) {
  const mapRu = {
    paid: "Оплачен",
    pending: "Ожидает оплаты",
    failed: "Ошибка",
    canceled: "Отменен",
  };
  const mapEn = {
    paid: "Paid",
    pending: "Pending",
    failed: "Failed",
    canceled: "Canceled",
  };
  return (lang === "ru" ? mapRu : mapEn)[status] || status;
}

export default function BillingPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];
  const locale = lang === "ru" ? "ru-RU" : "en-US";

  const [seats, setSeats] = useState(10);
  const [companyName, setCompanyName] = useState("");
  const [orders, setOrders] = useState([]);
  const [busyPlan, setBusyPlan] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const selectedTier = useMemo(() => getTierForSeats(seats), [seats]);

  async function loadOrders() {
    if (!API) return;
    try {
      const response = await fetch(`${API}/api/billing/training-orders`);
      if (!response.ok) return;
      const data = await response.json();
      setOrders(Array.isArray(data) ? data : []);
    } catch (_e) {
      // Orders are optional for first launch.
    }
  }

  useEffect(() => {
    loadOrders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createCheckout({ planCode, seatsCount, company }) {
    if (!API) {
      setError(t.pricing.payError);
      return;
    }

    setBusyPlan(planCode);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API}/api/billing/training-orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan_code: planCode,
          seats: seatsCount,
          company_name: company || undefined,
          success_url: `${window.location.origin}/billing/success`,
          cancel_url: `${window.location.origin}/billing/cancel`,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || t.pricing.payError);

      setMessage(t.pricing.paymentPending);
      await loadOrders();

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusyPlan("");
    }
  }

  return (
    <main className="page-shell">
      <AppNav title={t.pricing.title} subtitle={t.pricing.subtitle} />

      <section className="card glow">
        <h2>{t.pricing.individualTitle}</h2>
        <p className="muted">{t.pricing.individualLabel}</p>
        <p className="price-big">{formatRub(INDIVIDUAL_PRICE, locale)}</p>
        <p className="muted">{t.pricing.individualHint}</p>
        <button
          type="button"
          className="btn"
          disabled={busyPlan === "individual"}
          onClick={() => createCheckout({ planCode: "individual", seatsCount: 1, company: companyName })}
        >
          {busyPlan === "individual" ? t.common.loading : t.pricing.payNow}
        </button>
      </section>

      <section className="card">
        <h2>{t.pricing.companyTitle}</h2>
        <p className="muted">{t.pricing.companyHint}</p>

        <div className="grid grid-4">
          {corporateTiers.map((tier) => (
            <article key={tier.id} className={selectedTier.id === tier.id ? "feature-card active" : "feature-card"}>
              <h3>{tier.label[lang]}</h3>
              <p className="price-small">{formatRub(tier.priceRub, locale)}</p>
              <p className="muted">
                1-{tier.maxSeats} {t.common.seats}
              </p>
            </article>
          ))}
        </div>

        <div className="card" style={{ marginTop: 14 }}>
          <label>{t.pricing.seatsCalc}</label>
          <input
            className="input"
            type="number"
            min={1}
            max={100}
            value={seats}
            onChange={(event) => setSeats(Number(event.target.value || 1))}
          />

          <label style={{ marginTop: 10 }}>{t.pricing.companyName}</label>
          <input
            className="input"
            value={companyName}
            onChange={(event) => setCompanyName(event.target.value)}
            placeholder={lang === "ru" ? "Например, Altera Group" : "For example, Altera Group"}
          />

          <p className="muted" style={{ marginTop: 10 }}>
            {t.pricing.recommended}: <strong>{selectedTier.label[lang]}</strong> - {formatRub(selectedTier.priceRub, locale)}
          </p>

          <button
            type="button"
            className="btn btn-secondary"
            disabled={busyPlan === selectedTier.id}
            onClick={() =>
              createCheckout({
                planCode: selectedTier.id,
                seatsCount: seats,
                company: companyName,
              })
            }
          >
            {busyPlan === selectedTier.id ? t.common.loading : t.pricing.payNow}
          </button>
        </div>
      </section>

      <section className="card">
        <h2>{t.pricing.includedTitle}</h2>
        <ul className="check-list">
          {t.pricing.included.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      {(error || message) && (
        <section className="card">
          {error && <p className="error">{error}</p>}
          {message && <p className="muted">{message}</p>}
        </section>
      )}

      <section className="card">
        <h2>{t.pricing.ordersTitle}</h2>
        {orders.length === 0 ? (
          <p className="muted">{t.common.noData}</p>
        ) : (
          <ul className="order-list">
            {orders.slice(0, 6).map((order) => (
              <li key={order.id}>
                <span>
                  <strong>{order.plan_code}</strong> · {order.seats} {t.common.seats}
                </span>
                <span>
                  {formatRub(order.price_rub, locale)} · {t.pricing.orderStatus}: {statusLabel(order.status, lang)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
