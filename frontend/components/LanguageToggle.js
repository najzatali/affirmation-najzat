"use client";

import { useLanguage } from "./LanguageContext";

export default function LanguageToggle(props) {
  const ctx = useLanguage();
  const lang = props?.lang ?? ctx.lang;
  const setLang = props?.setLang ?? ctx.setLang;

  return (
    <div className="lang-toggle" role="group" aria-label="Language switcher">
      <button
        type="button"
        className={lang === "ru" ? "lang-btn active" : "lang-btn"}
        onClick={() => setLang("ru")}
        aria-pressed={lang === "ru"}
      >
        RU
      </button>
      <button
        type="button"
        className={lang === "en" ? "lang-btn active" : "lang-btn"}
        onClick={() => setLang("en")}
        aria-pressed={lang === "en"}
      >
        EN
      </button>
    </div>
  );
}
