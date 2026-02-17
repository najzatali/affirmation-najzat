"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "./LanguageContext";
import { i18n } from "../lib/i18n";
import LanguageToggle from "./LanguageToggle";
import BrandLogo from "./BrandLogo";

export default function AppNav({ title, subtitle }) {
  const pathname = usePathname();
  const { lang } = useLanguage();
  const t = i18n[lang];

  const navItems = [
    { href: "/", label: t.nav.home },
    { href: "/onboarding", label: t.nav.personalize },
    { href: "/library", label: t.nav.library },
    { href: "/record", label: t.nav.learning },
    { href: "/billing", label: t.nav.pricing },
  ];

  return (
    <header className="site-header">
      <div className="brand-row">
        <div>
          <BrandLogo />
          {title && <h1>{title}</h1>}
          {subtitle && <p className="muted subtitle">{subtitle}</p>}
        </div>
        <LanguageToggle />
      </div>

      <nav className="top-nav" aria-label="Main navigation">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={active ? "nav-link active" : "nav-link"}>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
