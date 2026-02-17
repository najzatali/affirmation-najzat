const PROFILE_KEY = "academy_profile_v1";
const PATH_KEY = "academy_path_v1";
const PROGRESS_KEY = "academy_progress_v1";

function defaultProgress() {
  return {
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
}

function isBrowser() {
  return typeof window !== "undefined" && Boolean(window.localStorage);
}

export function saveProfile(profile) {
  if (!isBrowser()) return;
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function readProfile() {
  if (!isBrowser()) return null;
  try {
    return JSON.parse(window.localStorage.getItem(PROFILE_KEY) || "null");
  } catch (_e) {
    return null;
  }
}

export function savePath(path) {
  if (!isBrowser()) return;
  window.localStorage.setItem(PATH_KEY, JSON.stringify(path));
}

export function readPath() {
  if (!isBrowser()) return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(PATH_KEY) || "[]");
    return Array.isArray(parsed) ? parsed : [];
  } catch (_e) {
    return [];
  }
}

export function saveProgress(progress) {
  if (!isBrowser()) return;
  window.localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
}

export function readProgress() {
  if (!isBrowser()) {
    return defaultProgress();
  }
  try {
    const parsed = JSON.parse(window.localStorage.getItem(PROGRESS_KEY) || "{}");
    return {
      completed: Array.isArray(parsed.completed) ? parsed.completed : [],
      xp: Number(parsed.xp || 0),
      gems: Number(parsed.gems || 0),
      hearts: Math.max(0, Math.min(5, Number(parsed.hearts ?? 5))),
      streak: Math.max(0, Number(parsed.streak || 0)),
      lastActiveDate: typeof parsed.lastActiveDate === "string" ? parsed.lastActiveDate : null,
      mode: parsed.mode || "text",
      currentModuleId: parsed.currentModuleId || null,
      segments: parsed.segments && typeof parsed.segments === "object" ? parsed.segments : {},
      visited: parsed.visited && typeof parsed.visited === "object" ? parsed.visited : {},
      tasks: parsed.tasks && typeof parsed.tasks === "object" ? parsed.tasks : {},
      practice: parsed.practice && typeof parsed.practice === "object" ? parsed.practice : {},
      coach: parsed.coach && typeof parsed.coach === "object" ? parsed.coach : {},
      dialog: parsed.dialog && typeof parsed.dialog === "object" ? parsed.dialog : {},
      steps: parsed.steps && typeof parsed.steps === "object" ? parsed.steps : {},
      stepXp: parsed.stepXp && typeof parsed.stepXp === "object" ? parsed.stepXp : {},
      mission: parsed.mission && typeof parsed.mission === "object" ? parsed.mission : {},
      missionReward: parsed.missionReward && typeof parsed.missionReward === "object" ? parsed.missionReward : {},
      blockQuiz: parsed.blockQuiz && typeof parsed.blockQuiz === "object" ? parsed.blockQuiz : {},
      quizReward: parsed.quizReward && typeof parsed.quizReward === "object" ? parsed.quizReward : {},
    };
  } catch (_e) {
    return defaultProgress();
  }
}

export function resetLearningState() {
  if (!isBrowser()) return;
  window.localStorage.removeItem(PROGRESS_KEY);
}
