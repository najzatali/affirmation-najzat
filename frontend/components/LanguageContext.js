"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

const LanguageContext = createContext({
  lang: "ru",
  setLang: () => {},
});

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState("ru");

  useEffect(() => {
    const saved = window.localStorage.getItem("app_lang");
    if (saved === "ru" || saved === "en") setLang(saved);
  }, []);

  useEffect(() => {
    window.localStorage.setItem("app_lang", lang);
  }, [lang]);

  const value = useMemo(() => ({ lang, setLang }), [lang]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  return useContext(LanguageContext);
}
