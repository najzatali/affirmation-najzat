"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { i18n } from "../../lib/i18n";
import {
  learningAgeGroups,
  learningFormats,
  learningGoals,
  learningIndustries,
  learningRoles,
} from "../../lib/learningCatalog";
import { diagnosticInterview, evaluateDiagnostic } from "../../lib/diagnosticInterview";
import { buildAdaptivePath, summarizePath } from "../../lib/personalization";
import { resetLearningState, savePath, saveProfile } from "../../lib/profileStorage";
import { formatRub, getTierForSeats } from "../../lib/pricing";

const DEFAULT_PROFILE = {
  learnerType: "individual",
  name: "",
  ageGroup: "young",
  industry: "general",
  role: "specialist",
  level: "beginner",
  format: "hybrid",
  goals: ["productivity", "quality"],
  seats: 5,
};

export default function OnboardingPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];
  const locale = lang === "ru" ? "ru-RU" : "en-US";

  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [goalError, setGoalError] = useState("");
  const [stage, setStage] = useState("profile");
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [coachFeedback, setCoachFeedback] = useState("");
  const [diagnostic, setDiagnostic] = useState(null);
  const [path, setPath] = useState([]);
  const [stats, setStats] = useState({ totalDurationMin: 0, totalXp: 0 });

  const questions = useMemo(() => diagnosticInterview[lang] || diagnosticInterview.ru, [lang]);
  const currentQuestion = questions[questionIndex] || null;

  const selectedTier = useMemo(() => getTierForSeats(profile.seats), [profile.seats]);
  const diagnosticProgress = questions.length > 0 ? Math.round((questionIndex / questions.length) * 100) : 0;

  function updateField(field, value) {
    setProfile((prev) => ({ ...prev, [field]: value }));
  }

  function toggleGoal(goalId) {
    setGoalError("");
    setProfile((prev) => {
      if (prev.goals.includes(goalId)) {
        return { ...prev, goals: prev.goals.filter((item) => item !== goalId) };
      }
      if (prev.goals.length >= 3) {
        setGoalError(t.onboarding.goalLimit);
        return prev;
      }
      return { ...prev, goals: [...prev.goals, goalId] };
    });
  }

  function startDiagnostic() {
    setGoalError("");
    setStage("diagnostic");
    setQuestionIndex(0);
    setAnswers({});
    setCoachFeedback("");
    setDiagnostic(null);
    setPath([]);
  }

  function selectAnswer(option) {
    if (!currentQuestion) return;
    setGoalError("");
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: option.value }));
    setCoachFeedback(option.coach);
  }

  function finishDiagnostic() {
    const report = evaluateDiagnostic(lang, answers);
    const prepared = {
      ...profile,
      level: report.levelId,
      diagnosticScore: report.scorePercent,
      diagnosticSummary: report.summary,
      recommendedStartModuleId: report.startModuleId,
      seats: Math.max(1, Number(profile.seats || 1)),
      generatedAt: new Date().toISOString(),
    };

    const adaptivePath = buildAdaptivePath(prepared, {
      maxModules: prepared.learnerType === "company" ? 16 : 14,
    });

    const pathStats = summarizePath(adaptivePath);

    saveProfile(prepared);
    savePath(adaptivePath);
    resetLearningState();

    setDiagnostic(report);
    setPath(adaptivePath);
    setStats(pathStats);
    setStage("result");
  }

  function nextQuestion() {
    if (!currentQuestion) return;
    const answer = answers[currentQuestion.id];
    if (answer === undefined || answer === null) {
      setGoalError(t.onboarding.answerRequired);
      return;
    }
    setGoalError("");

    if (questionIndex >= questions.length - 1) {
      finishDiagnostic();
      return;
    }

    setQuestionIndex((prev) => prev + 1);
    setCoachFeedback("");
  }

  return (
    <main className="page-shell">
      <AppNav title={t.onboarding.title} subtitle={t.onboarding.subtitle} />

      {stage === "profile" && (
        <section className="card">
          <div className="form-grid">
            <div>
              <label>{t.onboarding.learnerType}</label>
              <div className="option-grid">
                <button
                  type="button"
                  className={profile.learnerType === "individual" ? "option-card active" : "option-card"}
                  onClick={() => updateField("learnerType", "individual")}
                >
                  {t.onboarding.individual}
                </button>
                <button
                  type="button"
                  className={profile.learnerType === "company" ? "option-card active" : "option-card"}
                  onClick={() => updateField("learnerType", "company")}
                >
                  {t.onboarding.company}
                </button>
              </div>
            </div>

            <div>
              <label>{t.onboarding.name}</label>
              <input
                className="input"
                value={profile.name}
                onChange={(event) => updateField("name", event.target.value)}
                placeholder={lang === "ru" ? "Например, Nova Sales" : "For example, Nova Sales"}
              />
            </div>

            <div>
              <label>{t.onboarding.ageGroup}</label>
              <select className="select" value={profile.ageGroup} onChange={(event) => updateField("ageGroup", event.target.value)}>
                {learningAgeGroups.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label[lang]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>{t.onboarding.industry}</label>
              <select className="select" value={profile.industry} onChange={(event) => updateField("industry", event.target.value)}>
                {learningIndustries.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label[lang]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>{t.onboarding.role}</label>
              <select className="select" value={profile.role} onChange={(event) => updateField("role", event.target.value)}>
                {learningRoles.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label[lang]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>{t.onboarding.format}</label>
              <select className="select" value={profile.format} onChange={(event) => updateField("format", event.target.value)}>
                {learningFormats.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label[lang]}
                  </option>
                ))}
              </select>
            </div>

            {profile.learnerType === "company" && (
              <div>
                <label>{t.onboarding.seats}</label>
                <input
                  className="input"
                  type="number"
                  min={1}
                  max={100}
                  value={profile.seats}
                  onChange={(event) => updateField("seats", Number(event.target.value || 1))}
                />
                <p className="footnote">{t.onboarding.seatsHint}</p>
                <p className="muted">
                  {selectedTier.label[lang]}: <strong>{formatRub(selectedTier.priceRub, locale)}</strong>
                </p>
              </div>
            )}

            <div>
              <label>{t.onboarding.goals}</label>
              <div className="pill-row">
                {learningGoals.map((goal) => {
                  const active = profile.goals.includes(goal.id);
                  return (
                    <button
                      type="button"
                      key={goal.id}
                      className={active ? "area-pill active" : "area-pill"}
                      onClick={() => toggleGoal(goal.id)}
                    >
                      {goal.label[lang]}
                    </button>
                  );
                })}
              </div>
              {goalError && <p className="error">{goalError}</p>}
            </div>
          </div>

          <div className="hero-actions" style={{ marginTop: 18 }}>
            <button type="button" className="btn" onClick={startDiagnostic}>
              {t.onboarding.startDiagnostic}
            </button>
          </div>
        </section>
      )}

      {stage === "diagnostic" && currentQuestion && (
        <section className="card glow">
          <h2>{t.onboarding.diagnosticTitle}</h2>
          <p className="muted">{t.onboarding.diagnosticHint}</p>

          <div className="progress-line" style={{ marginBottom: 10 }}>
            <div className="progress-bar" style={{ width: `${diagnosticProgress}%` }} />
          </div>

          <p className="muted" style={{ marginTop: 0 }}>
            {t.onboarding.question} {questionIndex + 1} {t.onboarding.of} {questions.length}
          </p>

          <h3>{currentQuestion.prompt}</h3>

          <div className="option-grid">
            {currentQuestion.options.map((option) => {
              const active = answers[currentQuestion.id] === option.value;
              return (
                <button
                  key={`${currentQuestion.id}-${option.value}`}
                  type="button"
                  className={active ? "option-card active" : "option-card"}
                  onClick={() => selectAnswer(option)}
                >
                  {option.label}
                </button>
              );
            })}
          </div>

          {coachFeedback && (
            <p className="muted" style={{ marginTop: 12 }}>
              <strong>{t.onboarding.coachFeedback}:</strong> {coachFeedback}
            </p>
          )}

          {goalError && <p className="error">{goalError}</p>}

          <div className="hero-actions" style={{ marginTop: 14 }}>
            <button type="button" className="btn" onClick={nextQuestion}>
              {questionIndex >= questions.length - 1 ? t.onboarding.finishDiagnostic : t.onboarding.nextQuestion}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setStage("profile")}>
              {t.onboarding.backToProfile}
            </button>
          </div>
        </section>
      )}

      {stage === "result" && path.length > 0 && (
        <section className="card glow">
          <h2>{t.onboarding.ready}</h2>
          <p className="muted">{diagnostic?.summary}</p>

          <div className="stats-strip">
            <article className="stat-chip">
              <strong>{profile.name || t.common.noData}</strong>
              <p className="muted">{t.onboarding.profile}</p>
            </article>
            <article className="stat-chip">
              <strong>{diagnostic?.scorePercent}%</strong>
              <p className="muted">{t.onboarding.scoreLabel}</p>
            </article>
            <article className="stat-chip">
              <strong>{diagnostic?.levelLabel}</strong>
              <p className="muted">{t.onboarding.suggestedLevel}</p>
            </article>
            <article className="stat-chip">
              <strong>
                {stats.totalDurationMin} {t.common.min}
              </strong>
              <p className="muted">{t.onboarding.totalTime}</p>
            </article>
            <article className="stat-chip">
              <strong>{stats.totalXp} XP</strong>
              <p className="muted">{t.onboarding.totalXp}</p>
            </article>
          </div>

          <h3 style={{ marginTop: 14 }}>{t.onboarding.buildInstructionsTitle}</h3>
          <ol>
            <li>{lang === "ru" ? "Иди по базовому порядку: карта AI -> промпт по частям -> итерации -> безопасность данных." : "Follow foundation order: AI map -> prompt structure -> iteration -> data safety."}</li>
            <li>{lang === "ru" ? "После каждого урока сразу применяй шаблон промпта на своей реальной задаче." : "After each lesson, run the module prompt template on your real task immediately."}</li>
            <li>{lang === "ru" ? "Формат урока: короткий шаг -> твой ответ -> проверка -> следующий шаг, затем практическая заметка." : "Lesson format: short step -> your answer -> check -> next step, then practice note."}</li>
          </ol>

          <div className="hero-actions">
            <Link className="btn" href="/record">
              {t.onboarding.openLearning}
            </Link>
            <Link className="btn btn-ghost" href="/library">
              {t.onboarding.openPath}
            </Link>
          </div>
        </section>
      )}

      <p className="footnote">
        <Link href="/">{t.common.backHome}</Link>
      </p>
    </main>
  );
}
