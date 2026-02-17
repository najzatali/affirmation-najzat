"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { i18n } from "../../lib/i18n";
import { summarizePath } from "../../lib/personalization";
import { readPath, readProfile, readProgress } from "../../lib/profileStorage";

export default function LibraryPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  const [path, setPath] = useState([]);
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    setPath(readPath());
    setProfile(readProfile());
    setProgress(readProgress());
  }, []);

  const stats = useMemo(() => summarizePath(path), [path]);
  const completedIds = useMemo(() => new Set(progress?.completed || []), [progress?.completed]);

  const unlockedIds = useMemo(() => {
    const set = new Set();
    for (const module of path) {
      set.add(module.id);
      if (!completedIds.has(module.id)) break;
    }
    return set;
  }, [path, completedIds]);

  const currentModuleId = useMemo(() => {
    if (!path.length) return null;
    const firstOpen = path.find((module) => !completedIds.has(module.id));
    return firstOpen?.id || path[path.length - 1]?.id || null;
  }, [path, completedIds]);

  const completionPct = path.length ? Math.round(((progress?.completed?.length || 0) / path.length) * 100) : 0;

  return (
    <main className="page-shell">
      <AppNav title={t.library.title} subtitle={t.library.subtitle} />

      {path.length === 0 ? (
        <section className="card">
          <h2>{t.library.emptyTitle}</h2>
          <p className="muted">{t.library.emptyText}</p>
          <Link className="btn" href="/onboarding">
            {t.library.toPersonalize}
          </Link>
        </section>
      ) : (
        <>
          <section className="card">
            <h2>{t.library.activeProfile}</h2>
            <div className="stats-strip">
              <article className="stat-chip">
                <strong>{profile?.name || t.common.noData}</strong>
                <p className="muted">{t.library.activeProfile}</p>
              </article>
              <article className="stat-chip">
                <strong>{path.length}</strong>
                <p className="muted">{t.library.modules}</p>
              </article>
              <article className="stat-chip">
                <strong>
                  {stats.totalDurationMin} {t.common.min}
                </strong>
                <p className="muted">{t.library.duration}</p>
              </article>
              <article className="stat-chip">
                <strong>{stats.totalXp} XP</strong>
                <p className="muted">{t.library.xp}</p>
              </article>
              <article className="stat-chip">
                <strong>{progress?.streak || 0}</strong>
                <p className="muted">{t.learning.streakTitle}</p>
              </article>
              <article className="stat-chip">
                <strong>{progress?.gems || 0}</strong>
                <p className="muted">{t.learning.gemsTitle}</p>
              </article>
            </div>

            <div className="progress-line" style={{ marginTop: 14 }}>
              <div className="progress-bar" style={{ width: `${completionPct}%` }} />
            </div>
            <p className="muted" style={{ marginTop: 8 }}>
              {completionPct}% {t.learning.completePct}
            </p>

            <div className="hero-actions" style={{ marginTop: 12 }}>
              <Link className="btn" href={currentModuleId ? `/record?module=${currentModuleId}` : "/record"}>
                {t.library.continuePath}
              </Link>
            </div>
          </section>

          <section className="card">
            <h2>{t.library.mapTitle}</h2>
            <p className="muted">{t.library.mapHint}</p>

            <div className="route-map">
              {path.map((module, index) => {
                const isCompleted = completedIds.has(module.id);
                const isUnlocked = unlockedIds.has(module.id);
                const isCurrent = currentModuleId === module.id;
                const nodeClass = [
                  "route-node",
                  isCompleted ? "done" : "",
                  isUnlocked ? "" : "locked",
                  isCurrent ? "current" : "",
                  index % 2 === 0 ? "left" : "right",
                ]
                  .join(" ")
                  .trim();

                return (
                  <article key={module.id} className={nodeClass}>
                    <div className="route-node-head">
                      <span className="route-order">{module.order}</span>
                      <p className="muted">
                        {t.library.day} {module.day}
                      </p>
                    </div>
                    <h3>{module.title?.[lang] || module.title?.ru}</h3>
                    <p className="muted">{module.summary?.[lang] || module.summary?.ru}</p>
                    <div className="meta-row">
                      <span>
                        {module.durationMin} {t.common.min}
                      </span>
                      <span>{module.xp} XP</span>
                    </div>

                    {isUnlocked ? (
                      <Link className="link-btn" href={`/record?module=${module.id}`}>
                        {isCompleted ? t.library.repeatModule : t.library.openModule}
                      </Link>
                    ) : (
                      <button type="button" className="btn btn-ghost" disabled>
                        {t.library.lockedModule}
                      </button>
                    )}
                  </article>
                );
              })}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
