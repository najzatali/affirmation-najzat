"use client";

import Link from "next/link";

import AppNav from "../components/AppNav";
import { useLanguage } from "../components/LanguageContext";
import { i18n } from "../lib/i18n";

export default function HomePage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  return (
    <main className="page-shell">
      <AppNav title={t.home.title} subtitle={t.home.subtitle} />

      <section className="card glow">
        <p className="badge">Affirmation Studio</p>
        <div className="hero-actions">
          <Link href="/onboarding" className="btn">
            {t.home.ctaPrimary}
          </Link>
          <Link href="/record" className="btn-ghost">
            {t.home.ctaSecondary}
          </Link>
        </div>

        <ul className="hero-list">
          {t.home.points.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>{lang === "ru" ? "Как это работает" : "How it works"}</h2>
        <div className="grid grid-3">
          <article className="qa-card">
            <h3>{lang === "ru" ? "1. Онбординг" : "1. Onboarding"}</h3>
            <p className="muted">
              {lang === "ru"
                ? "Выбираешь 1-3 сферы, отвечаешь на структурированные вопросы и получаешь сильный набор аффирмаций."
                : "Choose 1-3 areas, answer structured questions, and get high-quality affirmations."}
            </p>
          </article>
          <article className="qa-card">
            <h3>{lang === "ru" ? "2. Голос и музыка" : "2. Voice and music"}</h3>
            <p className="muted">
              {lang === "ru"
                ? "Выбираешь системный голос или загружаешь voice sample, затем слушаешь превью музыки."
                : "Choose a system voice or upload your voice sample, then preview music tracks."}
            </p>
          </article>
          <article className="qa-card">
            <h3>{lang === "ru" ? "3. MP3 результат" : "3. MP3 output"}</h3>
            <p className="muted">
              {lang === "ru"
                ? "Запускаешь генерацию, получаешь файл и решаешь: удалить после скачивания или хранить до 14 дней."
                : "Run generation, get file, then decide: delete after download or keep up to 14 days."}
            </p>
          </article>
        </div>
      </section>

      <section className="card">
        <h2>{lang === "ru" ? "Юридически и этически" : "Legal and ethical"}</h2>
        <ul className="check-list">
          <li>
            {lang === "ru"
              ? "Перед загрузкой voice sample требуется согласие на обработку голоса."
              : "Voice sample upload requires explicit consent."}
          </li>
          <li>
            {lang === "ru"
              ? "Есть удаление голоса и результатов через личный кабинет."
              : "Voice and generated data can be deleted from the account."}
          </li>
          <li>
            {lang === "ru"
              ? "Запрещена загрузка чужого голоса без разрешения."
              : "Uploading someone else's voice without permission is prohibited."}
          </li>
        </ul>
        <p className="footnote">{t.home.disclaimer}</p>
      </section>
    </main>
  );
}
