import { learningModules } from "./learningCatalog";

const FOUNDATION_MODULE_IDS = [
  "foundation-ai-map",
  "foundation-account-setup",
  "foundation-prompt-blueprint",
  "foundation-prompt-iteration",
  "foundation-data-safety",
  "foundation-image-prompting",
  "foundation-video-prompting",
  "foundation-code-with-ai",
];
const UNIVERSAL_CORE_IDS = [...FOUNDATION_MODULE_IDS, "core-fact-check"];
const COMPANY_CORE_IDS = [...UNIVERSAL_CORE_IDS, "business-payments-russia"];
const RECOMMENDED_IDS = ["modality-image-gen", "modality-video-gen", "core-ai-literacy", "core-prompt-framework"];

function scoreByTag(values, target, exactWeight, allWeight = 0) {
  if (!Array.isArray(values) || !target) return 0;
  if (values.includes(target)) return exactWeight;
  if (values.includes("all")) return allWeight;
  return 0;
}

function scoreByGoals(values, goals, exactWeight, allWeight = 0) {
  if (!Array.isArray(values) || !Array.isArray(goals)) return 0;
  return goals.reduce((sum, goal) => sum + scoreByTag(values, goal, exactWeight, allWeight), 0);
}

function scoreModule(module, profile) {
  const tags = module.tags || {};
  let score = 0;

  score += scoreByTag(tags.industries, profile.industry, 8, 3);
  score += scoreByTag(tags.roles, profile.role, 7, 3);
  score += scoreByTag(tags.levels, profile.level, 4, 2);
  score += scoreByTag(tags.ageGroups, profile.ageGroup, 4, 1);
  score += scoreByTag(tags.learnerTypes, profile.learnerType, 4, 0);
  score += scoreByGoals(tags.goals, profile.goals, 3, 1);

  if (profile.format === "hybrid") {
    if (
      scoreByTag(tags.formats, "hybrid", 3, 0) > 0 ||
      scoreByTag(tags.formats, "text", 2, 0) > 0 ||
      scoreByTag(tags.formats, "voice", 2, 0) > 0
    ) {
      score += 2;
    }
  } else {
    score += scoreByTag(tags.formats, profile.format, 3, 1);
  }

  return score;
}

export function buildAdaptivePath(profile, options = {}) {
  const fallbackModules = profile?.learnerType === "company" ? 16 : 14;
  const maxModules = options.maxModules ?? fallbackModules;

  const baseIds = profile?.learnerType === "company" ? COMPANY_CORE_IDS : UNIVERSAL_CORE_IDS;
  const baseModules = baseIds.map((id) => learningModules.find((m) => m.id === id)).filter(Boolean);
  const ranked = learningModules
    .filter((module) => !baseIds.includes(module.id))
    .map((module) => ({
      module,
      score: scoreModule(module, profile),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      return (b.module.xp || 0) - (a.module.xp || 0);
    })
    .map((item) => item.module);

  const selected = [...baseModules];
  for (const module of ranked) {
    if (selected.some((item) => item.id === module.id)) continue;
    selected.push(module);
    if (selected.length >= maxModules) break;
  }

  for (const id of RECOMMENDED_IDS) {
    if (selected.length >= maxModules) break;
    if (selected.some((item) => item.id === id)) continue;
    const found = learningModules.find((item) => item.id === id);
    if (found) selected.push(found);
  }

  const hasCapstone = selected.some((m) => m.id === "certification-capstone");
  if (!hasCapstone) {
    const capstone = learningModules.find((m) => m.id === "certification-capstone");
    if (capstone) {
      if (selected.length >= maxModules) {
        selected[selected.length - 1] = capstone;
      } else {
        selected.push(capstone);
      }
    }
  }

  return selected.map((module, index) => ({
    ...module,
    order: index + 1,
    day: Math.min(6, Math.floor(index / 3) + 1),
  }));
}

export function summarizePath(path) {
  const totalDurationMin = path.reduce((sum, item) => sum + (item.durationMin || 0), 0);
  const totalXp = path.reduce((sum, item) => sum + (item.xp || 0), 0);
  return { totalDurationMin, totalXp };
}

export function getModuleById(path, moduleId) {
  return path.find((item) => item.id === moduleId) || null;
}

export function getNextModule(path, moduleId) {
  const currentIndex = path.findIndex((item) => item.id === moduleId);
  if (currentIndex < 0 || currentIndex >= path.length - 1) return null;
  return path[currentIndex + 1];
}

export function getPrevModule(path, moduleId) {
  const currentIndex = path.findIndex((item) => item.id === moduleId);
  if (currentIndex <= 0) return null;
  return path[currentIndex - 1];
}
