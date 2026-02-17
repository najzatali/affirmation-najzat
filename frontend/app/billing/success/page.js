"use client";

import Link from "next/link";

import AppNav from "../../../components/AppNav";
import { useLanguage } from "../../../components/LanguageContext";

export default function BillingSuccessPage() {
  const { lang } = useLanguage();

  return (
    <main className="page-shell">
      <AppNav
        title={lang === "ru" ? "Оплата подтверждена" : "Payment confirmed"}
        subtitle={lang === "ru" ? "Пакет активирован. Можно возвращаться к генерации аудио." : "Your package is active. You can continue with audio generation."}
      />
      <section className="card glow">
        <div className="hero-actions">
          <Link className="btn" href="/record">
            {lang === "ru" ? "Перейти к аудио" : "Go to audio"}
          </Link>
          <Link className="btn-ghost" href="/billing">
            {lang === "ru" ? "К тарифам" : "Back to plans"}
          </Link>
        </div>
      </section>
    </main>
  );
}
