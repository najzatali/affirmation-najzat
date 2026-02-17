"use client";

import Link from "next/link";
import AppNav from "../../../components/AppNav";
import { useLanguage } from "../../../components/LanguageContext";
import { i18n } from "../../../lib/i18n";

export default function BillingCancelPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  return (
    <main className="page-shell">
      <AppNav title={t.pricing.cancelTitle} subtitle={t.pricing.cancelText} />
      <section className="card">
        <h2>{t.pricing.cancelTitle}</h2>
        <p className="muted">{t.pricing.cancelText}</p>
        <div className="hero-actions">
          <Link className="btn" href="/billing">
            {t.nav.pricing}
          </Link>
          <Link className="btn btn-ghost" href="/">
            {t.common.backHome}
          </Link>
        </div>
      </section>
    </main>
  );
}
