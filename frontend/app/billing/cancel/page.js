"use client";

import Link from "next/link";

import AppNav from "../../../components/AppNav";
import { useLanguage } from "../../../components/LanguageContext";

export default function BillingCancelPage() {
  const { lang } = useLanguage();

  return (
    <main className="page-shell">
      <AppNav
        title={lang === "ru" ? "Оплата отменена" : "Payment canceled"}
        subtitle={lang === "ru" ? "Покупка не завершена. Можно попробовать еще раз." : "Checkout was not completed. You can try again."}
      />
      <section className="card">
        <div className="hero-actions">
          <Link className="btn" href="/billing">
            {lang === "ru" ? "Вернуться к тарифам" : "Back to plans"}
          </Link>
          <Link className="btn-ghost" href="/">
            {lang === "ru" ? "На главную" : "Home"}
          </Link>
        </div>
      </section>
    </main>
  );
}
