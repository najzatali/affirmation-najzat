"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { apiPost } from "../../lib/api";
import { i18n } from "../../lib/i18n";
import { areasCatalog, onboardingQuestionBlocks } from "../../lib/onboardingQuestions";
import { pushHistory, saveSession } from "../../lib/studioStorage";

function sessionTitle(lang, name) {
  const now = new Date();
  if (lang === "ru") {
    return `Сессия ${name} - ${now.toLocaleString("ru-RU")}`;
  }
  return `Session ${name} - ${now.toLocaleString("en-US")}`;
}

export default function OnboardingPage() {
  const router = useRouter();
  const { lang } = useLanguage();
  const t = i18n[lang];

  const areas = areasCatalog[lang] || [];
  const blocks = onboardingQuestionBlocks[lang] || { perArea: [], global: [] };

  const [userName, setUserName] = useState("");
  const [selectedAreas, setSelectedAreas] = useState(["health"]);
  const [started, setStarted] = useState(false);
  const [answers, setAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [error, setError] = useState("");

  const [busy, setBusy] = useState(false);
  const [affirmations, setAffirmations] = useState([]);
  const [projectId, setProjectId] = useState("");
  const [editorText, setEditorText] = useState("");

  const questionPlan = useMemo(() => {
    const plan = [];

    for (const areaId of selectedAreas) {
      const areaTitle = areas.find((item) => item.id === areaId)?.title || areaId;
      for (const question of blocks.perArea || []) {
        plan.push({
          ...question,
          areaId,
          areaTitle,
          questionId: `${areaId}:${question.key}`,
          text: question.text.replace("{area}", areaTitle.toLowerCase()),
        });
      }
    }

    for (const question of blocks.global || []) {
      plan.push({
        ...question,
        areaId: "global",
        areaTitle: lang === "ru" ? "Общий контекст" : "Global context",
        questionId: `global:${question.key}`,
        text: question.text,
      });
    }

    return plan;
  }, [areas, blocks.global, blocks.perArea, lang, selectedAreas]);

  const current = questionPlan[currentIndex] || null;
  const progress = questionPlan.length > 0 ? Math.round(((currentIndex + 1) / questionPlan.length) * 100) : 0;

  function updateAnswer(questionId, value) {
    setAnswers((prev) => ({ ...prev, [questionId]: String(value || "") }));
  }

  function toggleArea(areaId) {
    setError("");
    setSelectedAreas((prev) => {
      if (prev.includes(areaId)) {
        return prev.filter((item) => item !== areaId);
      }
      if (prev.length >= 3) {
        setError(t.onboarding.validationAreaLimit);
        return prev;
      }
      return [...prev, areaId];
    });
  }

  function startFlow() {
    if (!userName.trim()) {
      setError(lang === "ru" ? "Укажи имя" : "Please enter your name");
      return;
    }

    if (selectedAreas.length === 0) {
      setError(t.onboarding.validationAreas);
      return;
    }

    setError("");
    setStarted(true);
    setCurrentIndex(0);
    setAffirmations([]);
    setEditorText("");
  }

  function goNext() {
    if (!current) return;

    const value = (answers[current.questionId] || "").trim();
    if (!value) {
      setError(t.onboarding.validationAnswer);
      return;
    }

    setError("");
    setCurrentIndex((prev) => Math.min(prev + 1, questionPlan.length - 1));
  }

  function goBack() {
    setError("");
    setCurrentIndex((prev) => Math.max(0, prev - 1));
  }

  function buildGoalsPayload() {
    const globalQuestions = (blocks.global || []).map((item) => ({
      ...item,
      answer: String(answers[`global:${item.key}`] || "").trim(),
    }));

    const goals = [];

    for (const areaId of selectedAreas) {
      const areaQuestions = (blocks.perArea || []).map((item) => ({
        ...item,
        answer: String(answers[`${areaId}:${item.key}`] || "").trim(),
      }));

      for (const q of areaQuestions) {
        goals.push({
          area: areaId,
          key: q.key,
          prompt: q.text,
          answer: q.answer,
        });
      }

      for (const q of globalQuestions) {
        goals.push({
          area: areaId,
          key: q.key,
          prompt: q.text,
          answer: q.answer,
        });
      }
    }

    return goals;
  }

  async function generateAffirmations() {
    setError("");

    for (const item of questionPlan) {
      const value = (answers[item.questionId] || "").trim();
      if (!value) {
        setError(t.onboarding.validationAnswer);
        return;
      }
    }

    setBusy(true);
    try {
      const project = await apiPost("/api/projects", {
        title: sessionTitle(lang, userName.trim()),
        language: lang,
      });

      const goals = buildGoalsPayload();

      const generated = await apiPost("/api/affirmations/generate", {
        language: lang,
        tone: "calm",
        user_name: userName.trim(),
        goals,
      });

      const lines = Array.isArray(generated.affirmations) ? generated.affirmations : [];
      setProjectId(project.id);
      setAffirmations(lines);
      setEditorText(lines.join("\n"));

      saveSession({
        projectId: project.id,
        userName: userName.trim(),
        language: lang,
        areas: selectedAreas,
        goals,
        affirmations: lines,
        createdAt: new Date().toISOString(),
      });

      pushHistory({
        id: `${Date.now()}`,
        createdAt: new Date().toISOString(),
        userName: userName.trim(),
        areas: selectedAreas,
        status: "text_ready",
        durationSec: null,
        language: lang,
        projectId: project.id,
        affirmations: lines,
      });
    } catch (e) {
      setError(String(e?.message || t.common.errorDefault));
    } finally {
      setBusy(false);
    }
  }

  function continueToAudio() {
    const lines = editorText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    if (lines.length === 0) {
      setError(t.onboarding.validationAnswer);
      return;
    }

    saveSession({
      projectId,
      userName: userName.trim(),
      language: lang,
      areas: selectedAreas,
      goals: buildGoalsPayload(),
      affirmations: lines,
      createdAt: new Date().toISOString(),
    });

    router.push("/record");
  }

  return (
    <main className="page-shell">
      <AppNav title={t.onboarding.title} subtitle={t.onboarding.subtitle} />

      {!started && (
        <section className="card glow">
          <h2>{lang === "ru" ? "1) Как тебя зовут?" : "1) What is your name?"}</h2>
          <input
            className="input"
            placeholder={lang === "ru" ? "Например: Айзат" : "For example: Ajzat"}
            value={userName}
            onChange={(event) => setUserName(event.target.value)}
          />

          <h2 style={{ marginTop: 16 }}>{t.onboarding.chooseAreas}</h2>
          <p className="muted">{t.onboarding.areasHint}</p>

          <div className="pill-row" style={{ marginTop: 10 }}>
            {areas.map((area) => {
              const active = selectedAreas.includes(area.id);
              return (
                <button
                  key={area.id}
                  type="button"
                  className={active ? "area-pill active" : "area-pill"}
                  onClick={() => toggleArea(area.id)}
                >
                  {area.title}
                </button>
              );
            })}
          </div>

          <p className="footnote">
            {t.onboarding.selectedAreas}: <strong>{selectedAreas.length}</strong>
          </p>

          <div className="hero-actions">
            <button type="button" className="btn" onClick={startFlow}>
              {lang === "ru" ? "Начать короткий онбординг" : "Start quick onboarding"}
            </button>
          </div>
        </section>
      )}

      {started && current && affirmations.length === 0 && (
        <section className="card">
          <div className="progress-line">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
          </div>

          <p className="muted" style={{ marginTop: 8 }}>
            {lang === "ru" ? `${userName}, ` : `${userName}, `}
            {t.onboarding.questionStep} {currentIndex + 1} {t.onboarding.of} {questionPlan.length}
          </p>

          <article className="qa-card">
            <h3>{current.areaTitle}</h3>
            <p>{current.text}</p>

            {current.type === "scale" ? (
              <div className="pill-row" style={{ marginTop: 10 }}>
                {Array.from({ length: 10 }).map((_, index) => {
                  const value = String(index + 1);
                  const active = (answers[current.questionId] || "") === value;
                  return (
                    <button
                      type="button"
                      key={value}
                      className={active ? "area-pill active" : "area-pill"}
                      onClick={() => updateAnswer(current.questionId, value)}
                    >
                      {value}
                    </button>
                  );
                })}
              </div>
            ) : (
              <>
                <textarea
                  className="textarea"
                  value={answers[current.questionId] || ""}
                  onChange={(event) => updateAnswer(current.questionId, event.target.value)}
                />

                <p className="footnote">{t.onboarding.suggestions}</p>
                <div className="suggestion-row">
                  {(current.suggestions || []).map((item) => (
                    <button
                      type="button"
                      key={item}
                      className="suggestion-chip"
                      onClick={() => updateAnswer(current.questionId, item)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </>
            )}
          </article>

          <div className="hero-actions">
            <button type="button" className="btn-ghost" disabled={currentIndex === 0} onClick={goBack}>
              {t.common.back}
            </button>

            {currentIndex < questionPlan.length - 1 ? (
              <button type="button" className="btn" onClick={goNext}>
                {t.common.next}
              </button>
            ) : (
              <button type="button" className="btn-secondary" onClick={generateAffirmations} disabled={busy}>
                {busy ? t.onboarding.generating : t.onboarding.generate}
              </button>
            )}
          </div>
        </section>
      )}

      {affirmations.length > 0 && (
        <section className="card glow">
          <h2>
            {lang === "ru" ? `${userName}, твои аффирмации готовы` : `${userName}, your affirmations are ready`}
          </h2>
          <p className="muted">{t.onboarding.generatedHint}</p>

          <div className="result-box">
            <textarea className="textarea" value={editorText} onChange={(event) => setEditorText(event.target.value)} />
          </div>

          <div className="hero-actions">
            <button type="button" className="btn" onClick={continueToAudio}>
              {t.onboarding.continueToAudio}
            </button>
            <button type="button" className="btn-ghost" onClick={generateAffirmations} disabled={busy}>
              {busy ? t.onboarding.generating : t.onboarding.regenerate}
            </button>
          </div>

          <h3 style={{ marginTop: 14 }}>{t.onboarding.helperTitle}</h3>
          <ul className="check-list">
            {t.onboarding.helper.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>

          <p className="footnote">{t.onboarding.aiFootnote}</p>
        </section>
      )}

      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}
