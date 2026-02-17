"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import AppNav from "../../components/AppNav";
import { useLanguage } from "../../components/LanguageContext";
import { i18n } from "../../lib/i18n";
import { applyStreakUpdate, buildLessonPlan, countPassedSteps, evaluateStepQuiz, getModuleStepState } from "../../lib/lessonEngine";
import { getNextModule, getPrevModule } from "../../lib/personalization";
import { readPath, readProfile, readProgress, saveProgress } from "../../lib/profileStorage";

const API = process.env.NEXT_PUBLIC_API_URL;
const LEVEL_XP = 280;
const STEP_XP = 18;
const QUIZ_PASS_SCORE = 70;
const QUIZ_BONUS_XP = 32;
const QUIZ_BONUS_GEMS = 3;
const MISSION_BONUS_XP = 40;
const MISSION_BONUS_GEMS = 5;
const MODULE_BONUS_XP = 64;
const MODULE_BONUS_GEMS = 10;

const BASE_PROGRESS = {
  completed: [],
  xp: 0,
  gems: 0,
  hearts: 5,
  streak: 0,
  lastActiveDate: null,
  mode: "text",
  currentModuleId: null,
  segments: {},
  visited: {},
  tasks: {},
  practice: {},
  coach: {},
  dialog: {},
  steps: {},
  stepXp: {},
  mission: {},
  missionReward: {},
  blockQuiz: {},
  quizReward: {},
};

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function moduleOrderLabel(module, lang) {
  if (!module) return "";
  return lang === "ru" ? `День ${module.day}, модуль ${module.order}` : `Day ${module.day}, module ${module.order}`;
}

function buildPromptTemplate(module, lang, profile) {
  if (!module) return "";
  const role = profile?.role || (lang === "ru" ? "специалист" : "specialist");
  const industry = profile?.industry || (lang === "ru" ? "универсально" : "general");
  const title = module.title?.[lang] || module.title?.ru || module.id;

  if (lang === "ru") {
    return [
      `Задача: ${title}`,
      `Роль: Ты эксперт по направлению ${role}.`,
      `Контекст: Отрасль ${industry}, уровень пользователя ${profile?.level || "beginner"}.`,
      "Цель: Дай результат, который можно применить сегодня без лишней теории.",
      "Формат ответа: 1) короткий план, 2) готовый пример, 3) чеклист проверки.",
      "Ограничения: без персональных данных, без непроверенных фактов, без воды.",
      "Если данных не хватает, сначала задай до 3 уточняющих вопросов.",
    ].join("\n");
  }

  return [
    `Task: ${title}`,
    `Role: You are an expert for ${role}.`,
    `Context: Industry ${industry}, learner level ${profile?.level || "beginner"}.`,
    "Goal: Deliver something practical that can be used today.",
    "Output: 1) short plan, 2) ready-to-use example, 3) quality checklist.",
    "Constraints: no personal data, no unverified claims, no fluff.",
    "If context is missing, ask up to 3 clarifying questions first.",
  ].join("\n");
}

export default function LearningPage() {
  const { lang } = useLanguage();
  const t = i18n[lang];

  const [requestedModule, setRequestedModule] = useState(null);
  const [path, setPath] = useState([]);
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(BASE_PROGRESS);
  const [currentModuleId, setCurrentModuleId] = useState(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [speaking, setSpeaking] = useState(false);

  const [quizAnswers, setQuizAnswers] = useState({});
  const [theoryFeedback, setTheoryFeedback] = useState("");
  const [quizFeedback, setQuizFeedback] = useState("");
  const [templateMessage, setTemplateMessage] = useState("");

  const [missionFile, setMissionFile] = useState(null);
  const [missionDraft, setMissionDraft] = useState("");
  const [missionBusy, setMissionBusy] = useState(false);
  const [missionError, setMissionError] = useState("");
  const [missionResult, setMissionResult] = useState(null);
  const [helpDraft, setHelpDraft] = useState("");
  const [helpBusy, setHelpBusy] = useState(false);
  const [helpError, setHelpError] = useState("");
  const [helpMessages, setHelpMessages] = useState([]);

  const updateProgress = useCallback((updater) => {
    setProgress((prev) => {
      const next = typeof updater === "function" ? updater(prev) : updater;
      saveProgress(next);
      return next;
    });
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    setRequestedModule(url.searchParams.get("module"));
    setPath(readPath());
    setProfile(readProfile());
    setProgress({ ...BASE_PROGRESS, ...readProgress() });
  }, []);

  useEffect(() => {
    if (path.length === 0) return;
    const fallback = path[0]?.id || null;
    const firstIncomplete = path.find((item) => !progress.completed.includes(item.id))?.id || null;
    const recommended = profile?.recommendedStartModuleId || null;
    const startFrom = progress.completed.length > 0 ? firstIncomplete : recommended || firstIncomplete;
    const candidate = requestedModule || progress.currentModuleId || startFrom || fallback;
    const exists = path.some((item) => item.id === candidate);
    setCurrentModuleId(exists ? candidate : fallback);
  }, [path, requestedModule, progress.currentModuleId, progress.completed, profile?.recommendedStartModuleId]);

  const module = useMemo(() => path.find((item) => item.id === currentModuleId) || null, [path, currentModuleId]);
  const lessonPlan = useMemo(() => buildLessonPlan(module, lang, profile), [module, lang, profile]);
  const steps = lessonPlan.steps || [];
  const mission = lessonPlan.mission || { title: "", description: "", instructions: [], checkpoints: [], noteHint: "" };
  const step = steps[stepIndex] || null;

  const stepState = module ? getModuleStepState(progress, module.id) : {};
  const stepPassed = Boolean(stepState[stepIndex]);
  const passedCount = module ? countPassedSteps(progress, module.id, steps.length) : 0;
  const blockQuizState = module ? progress.blockQuiz?.[module.id] || null : null;
  const quizPassed = Boolean(blockQuizState?.passed);
  const quizScore = Number.isFinite(blockQuizState?.score) ? blockQuizState.score : null;
  const quizQuestions = useMemo(
    () =>
      steps
        .map((item, index) => ({ item, index }))
        .filter(({ item }) => item?.quiz && Array.isArray(item.quiz.options) && item.quiz.options.length > 0),
    [steps]
  );

  const promptTemplate = useMemo(() => buildPromptTemplate(module, lang, profile), [module, lang, profile]);

  useEffect(() => {
    if (!module) return;
    const savedSegment = Number(progress.segments?.[module.id] || 0);
    const firstUnpassed = steps.findIndex((_, idx) => !stepState[idx]);
    const preferred = firstUnpassed >= 0 ? firstUnpassed : savedSegment;
    const nextIndex = clamp(preferred, 0, Math.max(0, steps.length - 1));

    setStepIndex(nextIndex);
    setQuizAnswers(progress.blockQuiz?.[module.id]?.answers || {});
    setTheoryFeedback("");
    setQuizFeedback("");
    setMissionError("");
    setMissionFile(null);
    setMissionResult(progress.mission?.[module.id] || null);
    setMissionDraft(progress.practice?.[module.id] || "");
    setTemplateMessage("");
    setHelpDraft("");
    setHelpError("");
    setHelpMessages([
      {
        role: "assistant",
        text:
          lang === "ru"
            ? "Я рядом. Если застрял на шаге, напиши вопрос и я объясню, где ошибка и как исправить."
            : "I am here to help. Ask your question and I will explain what is wrong and how to fix it.",
      },
    ]);
  }, [module?.id, steps.length]);

  useEffect(() => {
    if (!module) return;
    updateProgress((prev) => {
      const previousSegment = Number(prev.segments?.[module.id] || 0);
      const sameModule = prev.currentModuleId === module.id;
      const sameSegment = previousSegment === stepIndex;
      if (sameModule && sameSegment) return prev;
      return {
        ...prev,
        currentModuleId: module.id,
        segments: {
          ...prev.segments,
          [module.id]: stepIndex,
        },
      };
    });
  }, [module?.id, stepIndex, updateProgress]);

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function stopVoice() {
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }

  function playVoice() {
    if (!step) return;
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    const text = `${lessonPlan.introScript || ""} ${step.title}. ${step.teaching}. ${step.action}`;
    stopVoice();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "ru" ? "ru-RU" : "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  }

  function setMode(mode) {
    updateProgress((prev) => ({ ...prev, mode }));
    if (mode === "text") stopVoice();
  }

  function restoreHearts() {
    updateProgress((prev) => ({ ...prev, hearts: 5 }));
    setTheoryFeedback(t.learning.heartsRestored);
  }

  function jumpStep(delta) {
    if (!steps.length) return;
    const next = clamp(stepIndex + delta, 0, steps.length - 1);
    setStepIndex(next);
    setTheoryFeedback("");
    if (progress.mode === "voice") stopVoice();
  }

  function loseHeart() {
    updateProgress((prev) => ({
      ...prev,
      hearts: Math.max(0, Number(prev.hearts ?? 5) - 1),
    }));
  }

  function markTheoryStepDone() {
    if (!module || !step) return;
    const alreadyPassed = Boolean(stepState[stepIndex]);

    updateProgress((prev) => {
      const streakBase = applyStreakUpdate(prev);
      const moduleSteps = streakBase.steps?.[module.id] && typeof streakBase.steps[module.id] === "object" ? { ...streakBase.steps[module.id] } : {};
      const moduleStepXp = streakBase.stepXp?.[module.id] && typeof streakBase.stepXp[module.id] === "object" ? { ...streakBase.stepXp[module.id] } : {};

      moduleSteps[stepIndex] = true;

      const alreadyRewarded = Boolean(moduleStepXp[stepIndex]);
      let nextXp = Number(streakBase.xp || 0);
      let nextGems = Number(streakBase.gems || 0);

      if (!alreadyRewarded) {
        moduleStepXp[stepIndex] = true;
        nextXp += STEP_XP;
        const passTotal = Object.keys(moduleSteps).filter((key) => moduleSteps[key]).length;
        if (passTotal % 3 === 0) nextGems += 1;
      }

      return {
        ...streakBase,
        xp: nextXp,
        gems: nextGems,
        hearts: alreadyPassed ? streakBase.hearts : Math.max(1, Number(streakBase.hearts ?? 5)),
        steps: {
          ...streakBase.steps,
          [module.id]: moduleSteps,
        },
        stepXp: {
          ...streakBase.stepXp,
          [module.id]: moduleStepXp,
        },
      };
    });

    setTheoryFeedback(alreadyPassed ? t.learning.theoryAlreadyDone : t.learning.theoryDone);
  }

  function submitBlockQuiz() {
    if (!module) return;
    if (passedCount < steps.length) {
      setQuizFeedback(t.learning.quizNeedTheory);
      return;
    }

    if (quizQuestions.length === 0) {
      setQuizFeedback(lang === "ru" ? "В этом модуле тест не требуется." : "This module has no quiz.");
      return;
    }

    const hasMissing = quizQuestions.some((_, idx) => quizAnswers[idx] === null || quizAnswers[idx] === undefined);
    if (hasMissing) {
      setQuizFeedback(t.learning.quizNeedAnswers);
      return;
    }

    let correct = 0;
    for (let idx = 0; idx < quizQuestions.length; idx += 1) {
      const question = quizQuestions[idx].item;
      const result = evaluateStepQuiz(question, quizAnswers[idx], lang);
      if (result.ok) correct += 1;
    }

    const score = Math.round((correct / quizQuestions.length) * 100);
    const passed = score >= QUIZ_PASS_SCORE;

    updateProgress((prev) => {
      const streakBase = applyStreakUpdate(prev);
      const previous = prev.blockQuiz?.[module.id] || {};
      const rewardAlreadyGiven = Boolean(prev.quizReward?.[module.id]);
      const wasPassed = Boolean(previous.passed);
      const finalPassed = passed || wasPassed;
      const bestScore = Math.max(Number(previous.score || 0), score);

      let nextXp = Number(streakBase.xp || 0);
      let nextGems = Number(streakBase.gems || 0);
      let nextHearts = Number(streakBase.hearts ?? 5);

      if (finalPassed && !rewardAlreadyGiven) {
        nextXp += QUIZ_BONUS_XP;
        nextGems += QUIZ_BONUS_GEMS;
      }

      if (!passed && !wasPassed) {
        nextHearts = Math.max(0, nextHearts - 1);
      }

      return {
        ...streakBase,
        xp: nextXp,
        gems: nextGems,
        hearts: nextHearts,
        blockQuiz: {
          ...(streakBase.blockQuiz || {}),
          [module.id]: {
            ...previous,
            passed: finalPassed,
            score: bestScore,
            total: quizQuestions.length,
            correct,
            answers: quizAnswers,
          },
        },
        quizReward: finalPassed
          ? {
              ...(streakBase.quizReward || {}),
              [module.id]: true,
            }
          : streakBase.quizReward || {},
      };
    });

    if (passed) {
      setQuizFeedback(`${t.learning.quizPassed}: ${score}%`);
      return;
    }
    if (quizPassed) {
      setQuizFeedback(`${t.learning.quizPassed}: ${quizScore ?? score}%`);
      return;
    }
    setQuizFeedback(`${t.learning.quizNotPassed}: ${score}%`);
  }

  async function verifyMission() {
    if (!module) return;
    if (!missionFile) {
      setMissionError(t.learning.missionNeedFile);
      return;
    }
    if ((missionDraft || "").trim().length < 20) {
      setMissionError(t.learning.missionNeedNote);
      return;
    }
    if (!API) {
      setMissionError(t.learning.coachApiMissing);
      return;
    }

    setMissionBusy(true);
    setMissionError("");

    try {
      const formData = new FormData();
      formData.append("language", lang);
      formData.append("module_title", module.title?.[lang] || module.title?.ru || module.id);
      formData.append("mission_title", mission.title || "Practice mission");
      formData.append("learner_note", missionDraft.trim());
      formData.append("required_checks", JSON.stringify(mission.checkpoints || []));
      formData.append("screenshot", missionFile);

      const response = await fetch(`${API}/api/coach/verify-screenshot`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || t.learning.missionVerifyError);
      }

      setMissionResult(data);
      updateProgress((prev) => {
        const next = {
          ...prev,
          practice: {
            ...prev.practice,
            [module.id]: missionDraft,
          },
          mission: {
            ...(prev.mission || {}),
            [module.id]: data,
          },
        };

        const rewarded = Boolean(prev.missionReward?.[module.id]);
        if (data.passed && !rewarded) {
          return {
            ...next,
            xp: Number(prev.xp || 0) + MISSION_BONUS_XP,
            gems: Number(prev.gems || 0) + MISSION_BONUS_GEMS,
            missionReward: {
              ...(prev.missionReward || {}),
              [module.id]: true,
            },
          };
        }

        return next;
      });

      if (!data.passed) {
        loseHeart();
      }
    } catch (error) {
      setMissionError(error instanceof Error ? error.message : t.learning.missionVerifyError);
    } finally {
      setMissionBusy(false);
    }
  }

  async function askHelp() {
    const question = (helpDraft || "").trim();
    if (question.length < 3) {
      setHelpError(t.learning.helpNeedQuestion);
      return;
    }

    const userMessage = { role: "user", text: question };
    setHelpMessages((prev) => [...prev, userMessage]);
    setHelpDraft("");
    setHelpError("");

    if (!API || !profile) {
      const fallbackText =
        lang === "ru"
          ? "Сформулируй цель, формат и ограничения. Затем отправь запрос снова и сравни ответ по точности."
          : "Define goal, output format, and constraints. Then resend your prompt and compare output quality.";
      setHelpMessages((prev) => [...prev, { role: "assistant", text: fallbackText }]);
      return;
    }

    setHelpBusy(true);
    try {
      const response = await fetch(`${API}/api/coach/help`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: lang,
          module_title: module?.title?.[lang] || module?.title?.ru || module?.id || "",
          step_title: step?.title || "",
          user_question: question,
          user_attempt: missionDraft || step?.action || "",
          profile: {
            learner_type: profile.learnerType || "individual",
            age_group: profile.ageGroup || "young",
            industry: profile.industry || "general",
            role: profile.role || "specialist",
            level: profile.level || "beginner",
            format: profile.format || "hybrid",
            goals: Array.isArray(profile.goals) ? profile.goals : [],
          },
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || t.learning.helpErrorDefault);
      }

      const assistantText = `${data.answer}\n\n${t.learning.helpWhatWrong}: ${data.what_wrong}\n${t.learning.helpHowFix}: ${data.how_fix}`;
      setHelpMessages((prev) => [...prev, { role: "assistant", text: assistantText }]);
    } catch (error) {
      setHelpError(error instanceof Error ? error.message : t.learning.helpErrorDefault);
    } finally {
      setHelpBusy(false);
    }
  }

  async function copyTemplate() {
    if (!promptTemplate) return;
    if (typeof window === "undefined" || !window.navigator?.clipboard) return;
    try {
      await window.navigator.clipboard.writeText(promptTemplate);
      setTemplateMessage(t.learning.templateCopied);
    } catch (_e) {
      setTemplateMessage(t.learning.templateCopyFailed);
    }
  }

  function openModule(targetModule) {
    if (!targetModule) return;
    stopVoice();
    setCurrentModuleId(targetModule.id);
  }

  function completeModule() {
    if (!module || !canCompleteModule) return;

    updateProgress((prev) => {
      const streakBase = applyStreakUpdate(prev);
      const already = streakBase.completed.includes(module.id);
      return {
        ...streakBase,
        completed: already ? streakBase.completed : [...streakBase.completed, module.id],
        xp: already ? streakBase.xp : streakBase.xp + MODULE_BONUS_XP,
        gems: already ? streakBase.gems : streakBase.gems + MODULE_BONUS_GEMS,
        hearts: Math.min(5, Number(streakBase.hearts ?? 5) + 1),
      };
    });

    const nextModule = getNextModule(path, module.id);
    if (nextModule) openModule(nextModule);
  }

  const completionPct = path.length > 0 ? Math.round((progress.completed.length / path.length) * 100) : 0;
  const level = Math.max(1, Math.floor(Number(progress.xp || 0) / LEVEL_XP) + 1);

  const prevModule = module ? getPrevModule(path, module.id) : null;
  const nextModule = module ? getNextModule(path, module.id) : null;

  const allStepsPassed = steps.length > 0 && passedCount >= steps.length;
  const missionPassed = Boolean(missionResult?.passed);
  const canCompleteModule = allStepsPassed && quizPassed && missionPassed;

  const moduleCheckpoints = [allStepsPassed, quizPassed, missionPassed];
  const moduleProgressPct = Math.round((moduleCheckpoints.filter(Boolean).length / moduleCheckpoints.length) * 100);

  const unlockedModuleIds = new Set();
  for (const item of path) {
    unlockedModuleIds.add(item.id);
    if (!progress.completed.includes(item.id)) break;
  }

  return (
    <main className="page-shell">
      <AppNav title={t.learning.title} subtitle={t.learning.subtitle} />

      {path.length === 0 || !module ? (
        <section className="card">
          <h2>{t.learning.noPathTitle}</h2>
          <p className="muted">{t.learning.noPathText}</p>
          <Link className="btn" href="/onboarding">
            {t.nav.personalize}
          </Link>
        </section>
      ) : (
        <>
          <section className="card duo-layout">
            <div className="duo-main">
              <p className="lesson-order">{moduleOrderLabel(module, lang)}</p>
              <h2>{module.title?.[lang] || module.title?.ru}</h2>
              <p className="muted">{module.summary?.[lang] || module.summary?.ru}</p>

              <article className="duo-card mentor-intro">
                <div className="mentor-avatar" aria-hidden="true">
                  <span>AI</span>
                </div>
                <div>
                  <h3>{t.learning.introTitle}</h3>
                  <p>{lessonPlan.introScript}</p>
                  <div className="player-controls">
                    <button
                      className={progress.mode === "text" ? "btn btn-secondary" : "btn btn-ghost"}
                      type="button"
                      onClick={() => setMode("text")}
                    >
                      {t.learning.textMode}
                    </button>
                    <button
                      className={progress.mode === "voice" ? "btn btn-secondary" : "btn btn-ghost"}
                      type="button"
                      onClick={() => setMode("voice")}
                    >
                      {t.learning.voiceMode}
                    </button>
                    {progress.mode === "voice" && (
                      <>
                        <button className="btn btn-ghost" type="button" onClick={playVoice}>
                          {t.learning.playVoice}
                        </button>
                        <button className="btn btn-ghost" type="button" onClick={stopVoice}>
                          {t.learning.stopVoice}
                        </button>
                        {speaking && <span className="pulse-dot" />}
                      </>
                    )}
                  </div>
                </div>
              </article>

              <div className="micro-progress" role="progressbar" aria-valuenow={moduleProgressPct} aria-valuemin={0} aria-valuemax={100}>
                <div className="micro-progress-fill" style={{ width: `${moduleProgressPct}%` }} />
              </div>
              <p className="muted" style={{ marginTop: 8 }}>
                {t.learning.theoryProgress}: {passedCount}/{steps.length} · {t.learning.progress}: {moduleProgressPct}%
              </p>

              <h3>{t.learning.blockTheoryTitle}</h3>
              {step && (
                <article className="duo-card">
                  <p className="muted">
                    {t.learning.step}: {Math.min(stepIndex + 1, steps.length)} / {steps.length}
                  </p>
                  <h3>{step.title}</h3>
                  <p>{step.teaching}</p>

                  <div className="lesson-subcard">
                    <h4>{t.learning.stepExampleTitle}</h4>
                    <p>{step.example}</p>
                  </div>

                  <div className="lesson-subcard">
                    <h4>{t.learning.stepActionTitle}</h4>
                    <p>{step.action}</p>
                    <p className="footnote">
                      <strong>{t.learning.stepAnswerHintLabel}:</strong> {step.answerHint}
                    </p>
                  </div>

                  <div className="player-controls">
                    <button type="button" className="btn" onClick={markTheoryStepDone}>
                      {t.learning.theoryMarkDone}
                    </button>
                    <span className={stepPassed ? "requirement-ok" : "footnote"}>
                      {stepPassed ? t.learning.theoryDoneLabel : t.learning.theoryPendingLabel}
                    </span>
                  </div>
                  {theoryFeedback && <p className={stepPassed ? "muted" : "error"}>{theoryFeedback}</p>}

                  <div className="player-controls">
                    <button className="btn btn-ghost" type="button" onClick={() => jumpStep(-1)}>
                      {t.learning.prev}
                    </button>
                    <button className="btn btn-ghost" type="button" onClick={() => jumpStep(1)}>
                      {t.learning.next}
                    </button>
                  </div>
                </article>
              )}

              <h3>{t.learning.blockQuizTitle}</h3>
              <article className="duo-card">
                <p className="muted">{t.learning.quizBlockHint}</p>
                {quizQuestions.map((question, questionIndex) => (
                  <div className="qa-box" key={`${question.item.id}-block-quiz`}>
                    <h4>
                      {t.learning.step} {question.index + 1}
                    </h4>
                    <p>{question.item.quiz.question}</p>
                    <div className="option-grid">
                      {question.item.quiz.options.map((option, optionIndex) => {
                        const active = quizAnswers[questionIndex] === optionIndex;
                        return (
                          <button
                            key={`${question.item.id}-option-${optionIndex}`}
                            type="button"
                            className={active ? "option-card active" : "option-card"}
                            onClick={() =>
                              setQuizAnswers((prev) => ({
                                ...prev,
                                [questionIndex]: optionIndex,
                              }))
                            }
                          >
                            {option}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
                <div className="player-controls">
                  <button className="btn" type="button" onClick={submitBlockQuiz}>
                    {t.learning.quizSubmit}
                  </button>
                  {quizPassed && quizScore !== null && (
                    <span className="requirement-ok">
                      {t.learning.quizPassed}: {quizScore}%
                    </span>
                  )}
                  {!quizPassed && quizScore !== null && (
                    <span className="requirement-pending">
                      {t.learning.quizNotPassed}: {quizScore}%
                    </span>
                  )}
                </div>
                {quizFeedback && <p className={quizPassed ? "muted" : "error"}>{quizFeedback}</p>}
              </article>

              <h3>{t.learning.blockPracticeTitle}</h3>
              <article className="duo-card">
                <h3>{mission.title || t.learning.missionBlockTitle}</h3>
                <p>{mission.description}</p>
                <h4>{t.learning.missionInstructionsTitle}</h4>
                <ol>
                  {(mission.instructions || []).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
                <h4>{t.learning.missionChecklistTitle}</h4>
                <ul className="requirements-list">
                  {(mission.checkpoints || []).map((item) => (
                    <li key={item} className="requirement-pending">
                      {item}
                    </li>
                  ))}
                </ul>

                <label style={{ marginTop: 8, display: "block" }}>{t.learning.missionUploadLabel}</label>
                <input
                  className="input"
                  type="file"
                  accept="image/*"
                  onChange={(event) => setMissionFile(event.target.files?.[0] || null)}
                />

                <label style={{ marginTop: 10, display: "block" }}>{t.learning.missionNoteLabel}</label>
                <textarea
                  className="textarea"
                  value={missionDraft}
                  onChange={(event) => setMissionDraft(event.target.value)}
                  placeholder={mission.noteHint || t.learning.missionNotePlaceholder}
                />

                <div className="player-controls">
                  <button type="button" className="btn" onClick={verifyMission} disabled={missionBusy}>
                    {missionBusy ? t.learning.missionVerifying : t.learning.missionVerify}
                  </button>
                </div>

                {missionError && <p className="error">{missionError}</p>}

                {missionResult && (
                  <div className={missionResult.passed ? "mission-result pass" : "mission-result fail"}>
                    <p>
                      <strong>{missionResult.passed ? t.learning.missionPassed : t.learning.missionNotPassed}</strong>
                    </p>
                    <p>
                      {t.learning.missionScore}: <strong>{missionResult.score}</strong>
                    </p>
                    <p>{missionResult.summary}</p>
                    {Array.isArray(missionResult.found) && missionResult.found.length > 0 && (
                      <>
                        <p>
                          <strong>{t.learning.missionFound}:</strong>
                        </p>
                        <ul className="requirements-list">
                          {missionResult.found.map((item) => (
                            <li key={item} className="requirement-ok">
                              {item}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                    {Array.isArray(missionResult.missing) && missionResult.missing.length > 0 && (
                      <>
                        <p>
                          <strong>{t.learning.missionMissing}:</strong>
                        </p>
                        <ul className="requirements-list">
                          {missionResult.missing.map((item) => (
                            <li key={item} className="requirement-pending">
                              {item}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                    <p>
                      <strong>{t.learning.missionNextAction}:</strong> {missionResult.next_action}
                    </p>
                  </div>
                )}
              </article>

              <h3>{t.learning.blockHelpTitle}</h3>
              <article className="duo-card">
                <p className="muted">{t.learning.blockHelpHint}</p>
                <div className="lesson-chat">
                  {helpMessages.map((message, index) => (
                    <div key={`${message.role}-${index}`} className={message.role === "assistant" ? "chat-bubble assistant" : "chat-bubble user"}>
                      <pre>{message.text}</pre>
                    </div>
                  ))}
                </div>
                <textarea
                  className="textarea"
                  value={helpDraft}
                  onChange={(event) => setHelpDraft(event.target.value)}
                  placeholder={t.learning.helpPlaceholder}
                />
                <div className="player-controls">
                  <button type="button" className="btn" onClick={askHelp} disabled={helpBusy}>
                    {helpBusy ? t.learning.helpLoading : t.learning.helpSend}
                  </button>
                </div>
                {helpError && <p className="error">{helpError}</p>}
              </article>

              <details className="details-block" style={{ marginTop: 12 }}>
                <summary>{t.learning.promptTemplateTitle}</summary>
                <p className="muted">{t.learning.promptTemplateHint}</p>
                <pre className="prompt-template">{promptTemplate}</pre>
                <div className="player-controls" style={{ marginTop: 8 }}>
                  <button type="button" className="btn btn-ghost" onClick={copyTemplate}>
                    {t.learning.copyTemplate}
                  </button>
                  {templateMessage && <span className="muted">{templateMessage}</span>}
                </div>
              </details>

              <ul className="requirements-list">
                <li className={allStepsPassed ? "requirement-ok" : "requirement-pending"}>
                  {t.learning.requirementSteps} ({passedCount}/{steps.length})
                </li>
                <li className={quizPassed ? "requirement-ok" : "requirement-pending"}>{t.learning.requirementQuiz}</li>
                <li className={missionPassed ? "requirement-ok" : "requirement-pending"}>{t.learning.requirementMission}</li>
              </ul>

              {!canCompleteModule && <p className="footnote">{t.learning.cannotCompleteHint}</p>}

              <div className="player-controls" style={{ marginTop: 14 }}>
                <button className="btn" type="button" onClick={completeModule} disabled={!canCompleteModule}>
                  {t.learning.complete}
                </button>
                <button className="btn btn-ghost" type="button" onClick={() => openModule(prevModule)} disabled={!prevModule}>
                  {t.learning.prevModule}
                </button>
                <button className="btn btn-ghost" type="button" onClick={() => openModule(nextModule)} disabled={!nextModule}>
                  {t.learning.nextModule}
                </button>
              </div>
            </div>

            <aside className="card duo-side">
              <h3>{t.learning.progress}</h3>
              <div className="progress-line">
                <div className="progress-bar" style={{ width: `${completionPct}%` }} />
              </div>
              <p className="muted">
                {completionPct}% {t.learning.completePct}
              </p>

              <div className="game-stats">
                <article>
                  <span>{t.learning.totalXp}</span>
                  <strong>{progress.xp}</strong>
                </article>
                <article>
                  <span>{t.learning.level}</span>
                  <strong>{level}</strong>
                </article>
                <article>
                  <span>{t.learning.streakTitle}</span>
                  <strong>{progress.streak || 0}</strong>
                </article>
                <article>
                  <span>{t.learning.gemsTitle}</span>
                  <strong>{progress.gems || 0}</strong>
                </article>
              </div>

              <div className="hearts-row">
                <span>{t.learning.heartsTitle}:</span>
                <strong>{progress.hearts ?? 5}/5</strong>
              </div>
              {(progress.hearts ?? 5) === 0 && (
                <>
                  <p className="error">{t.learning.heartsEmpty}</p>
                  <button className="btn btn-ghost" type="button" onClick={restoreHearts}>
                    {t.learning.restoreHearts}
                  </button>
                </>
              )}

              <p className="footnote" style={{ marginTop: 12 }}>
                +{QUIZ_BONUS_XP} XP / +{QUIZ_BONUS_GEMS} {t.learning.gemsTitle.toLowerCase()} {t.learning.quizRewardHint}
              </p>
              <p className="footnote">
                +{MISSION_BONUS_XP} XP / +{MISSION_BONUS_GEMS} {t.learning.gemsTitle.toLowerCase()} {t.learning.missionRewardHint}
              </p>
              <p className="footnote">
                +{MODULE_BONUS_XP} XP / +{MODULE_BONUS_GEMS} {t.learning.gemsTitle.toLowerCase()} {t.learning.moduleRewardHint}
              </p>

              <h3 style={{ marginTop: 18 }}>{t.learning.routeTitle}</h3>
              <div className="route-mini-list">
                {path.map((item) => {
                  const completed = progress.completed.includes(item.id);
                  const unlocked = unlockedModuleIds.has(item.id);
                  const active = item.id === module.id;
                  const className = ["route-mini-item", completed ? "done" : "", unlocked ? "" : "locked", active ? "active" : ""]
                    .join(" ")
                    .trim();

                  return (
                    <button
                      key={item.id}
                      type="button"
                      className={className}
                      onClick={() => (unlocked ? openModule(item) : null)}
                      disabled={!unlocked}
                      title={unlocked ? t.learning.routeOpen : t.learning.routeLocked}
                    >
                      <span>{item.order}</span>
                      <strong>{item.title?.[lang] || item.title?.ru}</strong>
                    </button>
                  );
                })}
              </div>
            </aside>
          </section>
        </>
      )}
    </main>
  );
}
