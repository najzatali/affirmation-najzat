"use client";

import Link from "next/link";
import AppNav from "../../../components/AppNav";
import { useLanguage } from "../../../components/LanguageContext";
import { i18n } from "../../../lib/i18n";

export default function BillingSuccessPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  return (
    <main className="page-shell">
      <AppNav title={t.pricing.successTitle} subtitle={t.pricing.successText} />
      <section className="card glow">
        <h2>{t.pricing.successTitle}</h2>
        <p className="muted">{t.pricing.successText}</p>
        <div className="hero-actions">
          <Link className="btn" href="/onboarding">
            {t.nav.personalize}
          </Link>
          <Link className="btn btn-ghost" href="/billing">
            {t.nav.pricing}
          </Link>
        </div>
      </section>
    </main>
  );
}
