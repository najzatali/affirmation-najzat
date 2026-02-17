const STOP_WORDS = {
  ru: new Set([
    "когда",
    "чтобы",
    "который",
    "которая",
    "которые",
    "можно",
    "нужно",
    "после",
    "перед",
    "этого",
    "этот",
    "также",
    "здесь",
    "такой",
    "будет",
    "должен",
  ]),
  en: new Set([
    "which",
    "there",
    "their",
    "about",
    "after",
    "before",
    "should",
    "would",
    "could",
    "this",
    "that",
    "with",
    "from",
    "into",
    "your",
  ]),
};

const ACTION_VERBS = {
  ru: /сделаю|применю|проверю|создам|запущу|использую|настрою|сравню|сохраню|выберу|соберу|напишу|пройду|зарегистрируюсь/,
  en: /i will|apply|check|create|build|run|use|compare|save|choose|write|configure|register/,
};

function normalizeWords(text) {
  return (text || "")
    .toLowerCase()
    .replace(/[^a-zA-Zа-яА-Я0-9\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function collectKeywords(text, lang) {
  const stop = STOP_WORDS[lang] || STOP_WORDS.ru;
  return Array.from(new Set(normalizeWords(text).filter((word) => word.length >= 5 && !stop.has(word)))).slice(0, 10);
}

function clip(text, maxLen = 260) {
  const cleaned = (text || "").trim();
  if (!cleaned) return "";
  if (cleaned.length <= maxLen) return cleaned;
  return `${cleaned.slice(0, maxLen - 1).trimEnd()}...`;
}

function makeStep({
  id,
  title,
  teaching,
  example,
  action,
  answerHint,
  answerExample,
  quizQuestion,
  quizOptions,
  quizCorrect,
  quizExplain,
  mustInclude,
  lang,
}) {
  const baseKeywords = collectKeywords(`${teaching} ${action} ${(mustInclude || []).join(" ")}`, lang);
  return {
    id,
    title,
    teaching,
    example,
    action,
    answerHint,
    answerExample,
    quiz: {
      question: quizQuestion,
      options: quizOptions,
      correctIndex: quizCorrect,
      explain: quizExplain,
    },
    keywords: baseKeywords,
  };
}

function lessonPresetAiMap(lang) {
  if (lang === "ru") {
    return {
      introScript:
        "Привет. Я твой AI-наставник. Сейчас без сложных слов разберем, какие бывают AI, где какой использовать, и сразу сделаем первую практику. После каждого шага ты пишешь короткий ответ по шаблону, а я проверяю.",
      steps: [
        makeStep({
          id: "ai-map-1",
          title: "Что такое AI простыми словами",
          teaching:
            "AI - это инструмент, который помогает быстрее думать, писать, создавать и проверять результат. Он не заменяет тебя, а ускоряет работу, если ты даешь ему понятную задачу.",
          example:
            "Пример: вместо 40 минут на черновик письма ты можешь получить базовый вариант за 2 минуты и доработать его вручную.",
          action:
            "Напиши, какую одну задачу ты хочешь ускорить с помощью AI уже сегодня.",
          answerHint: "Шаблон ответа: 'Я понял(а), что ... Для меня это полезно в ... Сейчас сделаю ...'",
          answerExample: "Я понял, что AI ускоряет черновую работу. Для меня это полезно в написании писем клиентам. Сейчас сделаю шаблон ответа на частые вопросы.",
          quizQuestion: "Главная роль AI в обучении на старте?",
          quizOptions: ["Полностью заменить человека", "Ускорить работу и повысить качество при проверке человеком", "Работать без цели и контекста"],
          quizCorrect: 1,
          quizExplain: "Верно: AI дает ускорение, но финальное решение и ответственность за человеком.",
          mustInclude: ["задачу", "сделаю", "полезно"],
          lang,
        }),
        makeStep({
          id: "ai-map-2",
          title: "Какие бывают AI и когда какой нужен",
          teaching:
            "Текстовый AI - для писем, идей, анализа и кода. Графический AI - для картинок и дизайна. Видео AI - для роликов и сцен. Голосовой AI - для озвучки и расшифровки.",
          example:
            "Пример выбора: нужно объяснить тему ученику - берешь текстовый AI. Нужно сделать обложку урока - графический AI.",
          action: "Выбери один тип AI под свою задачу и объясни почему.",
          answerHint: "Шаблон: 'Для задачи ... я выберу ... AI, потому что ...'",
          answerExample: "Для задачи подготовки поста я выберу текстовый AI, потому что мне нужен быстрый черновик и структура.",
          quizQuestion: "Какой AI подходит для создания обложки презентации?",
          quizOptions: ["Текстовый", "Графический", "Голосовой"],
          quizCorrect: 1,
          quizExplain: "Верно: визуальные материалы делает графический AI.",
          mustInclude: ["выберу", "потому", "задача"],
          lang,
        }),
        makeStep({
          id: "ai-map-3",
          title: "Как выбрать AI-инструмент без ошибок",
          teaching:
            "Правильная последовательность: 1) цель, 2) формат результата, 3) ограничения по качеству, времени и безопасности. Если пропустить шаги, ответ будет размытым.",
          example:
            "Пример формулировки: 'Цель - сделать план урока. Формат - таблица. Ограничение - до 5 пунктов, без непроверенных фактов'.",
          action: "Составь мини-запрос по этой формуле под свою задачу.",
          answerHint: "Шаблон: 'Цель: ... Формат: ... Ограничения: ...'",
          answerExample: "Цель: сделать описание курса. Формат: список из 5 блоков. Ограничения: простой язык, без сложных терминов.",
          quizQuestion: "Что должно быть первым в хорошем запросе?",
          quizOptions: ["Случайный длинный текст", "Цель задачи", "Только стиль ответа"],
          quizCorrect: 1,
          quizExplain: "Верно: сначала всегда цель, иначе модель угадывает, что тебе нужно.",
          mustInclude: ["цель", "формат", "ограничения"],
          lang,
        }),
      ],
      mission: {
        title: "Практика: первый рабочий результат в AI",
        description:
          "Задача: зайди в любой AI-сервис, запусти новый чат, отправь свой структурный запрос и получи ответ. Сделай скриншот экрана, где видно сервис, запрос и результат.",
        instructions: [
          "Открой браузер и зайди в выбранный AI-сервис.",
          "Нажми кнопку 'Новый чат' или 'New chat'.",
          "Вставь свой запрос по формуле: цель -> формат -> ограничения.",
          "Нажми отправить и дождись ответа.",
          "Сделай скриншот, где видно сервис, запрос и ответ.",
        ],
        checkpoints: [
          "Виден интерфейс AI-сервиса",
          "Виден твой запрос (цель/формат/ограничения)",
          "Виден полученный ответ",
          "Есть короткий комментарий: что получилось",
        ],
        noteHint: "Опиши 2-3 предложениями: какой сервис использовал, какой запрос отправил, какой получил результат.",
      },
    };
  }

  return {
    introScript:
      "Hi. I am your AI coach. In this lesson we keep it simple: AI types, when to use each one, and one real practice right away. After every step, answer briefly using the template and I will check it.",
    steps: [
      makeStep({
        id: "ai-map-1",
        title: "What AI means in plain language",
        teaching:
          "AI is a tool that helps you think, write, create, and review faster. It does not replace you. It speeds up execution when you provide a clear task.",
        example: "Example: instead of 40 minutes for a draft email, you can get version 1 in 2 minutes and refine it.",
        action: "Write one task you want to speed up with AI today.",
        answerHint: "Template: 'I understood that ... This helps me in ... Now I will ...'",
        answerExample: "I understood that AI speeds up first drafts. This helps me with client replies. Now I will build a reusable response template.",
        quizQuestion: "Main AI role for a beginner?",
        quizOptions: ["Fully replace the human", "Speed up work with human quality control", "Work without context"],
        quizCorrect: 1,
        quizExplain: "Correct: AI accelerates work, while final responsibility remains with the human.",
        mustInclude: ["task", "will", "help"],
        lang,
      }),
      makeStep({
        id: "ai-map-2",
        title: "AI types and when to use them",
        teaching:
          "Text AI is for writing, analysis, and code. Image AI is for visuals and design. Video AI is for scenes and clips. Voice AI is for speech and transcription.",
        example: "Example: explain a topic -> text AI. Create lesson cover -> image AI.",
        action: "Pick one AI type for your current task and explain why.",
        answerHint: "Template: 'For task ... I choose ... AI because ...'",
        answerExample: "For content drafting I choose text AI because I need structure and speed.",
        quizQuestion: "Which AI is best for a presentation cover image?",
        quizOptions: ["Text AI", "Image AI", "Voice AI"],
        quizCorrect: 1,
        quizExplain: "Correct: visual output requires image AI.",
        mustInclude: ["choose", "because", "task"],
        lang,
      }),
      makeStep({
        id: "ai-map-3",
        title: "How to choose a tool without mistakes",
        teaching:
          "Use this sequence: 1) goal, 2) output format, 3) constraints for quality, time, and safety. If you skip these, output becomes generic.",
        example: "Example request: 'Goal: lesson plan. Format: table. Constraints: max 5 points, no unverified facts'.",
        action: "Write a mini-request using that formula for your own task.",
        answerHint: "Template: 'Goal: ... Format: ... Constraints: ...'",
        answerExample: "Goal: outline course module. Format: 5-point list. Constraints: plain language, no fake facts.",
        quizQuestion: "What should come first in a strong request?",
        quizOptions: ["Random long text", "Task goal", "Style only"],
        quizCorrect: 1,
        quizExplain: "Correct: goal first, then everything else.",
        mustInclude: ["goal", "format", "constraints"],
        lang,
      }),
    ],
    mission: {
      title: "Practice: first real AI result",
      description:
        "Open any AI service, start a new chat, send your structured request, and get an output. Upload a screenshot where service, prompt, and output are visible.",
      instructions: [
        "Open your chosen AI service in browser.",
        "Click 'New chat'.",
        "Paste your prompt with goal, format, and constraints.",
        "Send it and wait for output.",
        "Take one screenshot with service, prompt, and output visible.",
      ],
      checkpoints: [
        "AI service interface is visible",
        "Your prompt is visible",
        "Generated output is visible",
        "Short learner comment is provided",
      ],
      noteHint: "Add 2-3 sentences: which service you used, what prompt you sent, what result you got.",
    },
  };
}

function lessonPresetAccountSetup(lang) {
  if (lang === "ru") {
    return {
      introScript:
        "Сейчас настроим старт правильно: выбор сервиса, регистрация, безопасность и первый запрос. В конце ты приложишь скриншот как подтверждение практики.",
      steps: [
        makeStep({
          id: "acc-1",
          title: "Выбор сервиса под задачу",
          teaching:
            "Не нужно регистрироваться во всех сервисах сразу. Выбери 1 текстовый и 1 визуальный инструмент под текущие задачи.",
          example: "Если цель - писать тексты и делать план урока, начинай с одного текстового сервиса.",
          action: "Напиши, какие 1-2 сервиса выберешь и под какие задачи.",
          answerHint: "Шаблон: 'Выбираю ... для ... и ... для ...'",
          answerExample: "Выбираю текстовый сервис для писем и планов. И графический сервис для обложек к урокам.",
          quizQuestion: "Лучший подход на старте?",
          quizOptions: ["Сразу 10 сервисов", "1-2 сервиса под конкретные задачи", "Сначала оплатить всё, потом разбираться"],
          quizCorrect: 1,
          quizExplain: "Верно: сначала узкий и понятный стек, потом расширение.",
          mustInclude: ["выбираю", "для", "задач"],
          lang,
        }),
        makeStep({
          id: "acc-2",
          title: "Регистрация и безопасность",
          teaching:
            "После регистрации сразу включай защиту: сложный пароль и двухфакторная авторизация. Рабочие доступы лучше хранить отдельно от личных.",
          example: "Мини-чеклист: рабочая почта, 2FA, сохраненный способ восстановления доступа.",
          action: "Опиши, какие 2 шага безопасности ты включишь сразу после регистрации.",
          answerHint: "Шаблон: 'Сразу включу ... и ...'",
          answerExample: "Сразу включу сложный пароль и двухфакторную авторизацию через приложение.",
          quizQuestion: "Что обязательно включить после регистрации?",
          quizOptions: ["Только красивый ник", "2FA и надежный пароль", "Ничего не настраивать"],
          quizCorrect: 1,
          quizExplain: "Верно: защита аккаунта обязательна с первого дня.",
          mustInclude: ["включу", "пароль", "двухфактор"],
          lang,
        }),
        makeStep({
          id: "acc-3",
          title: "Первый запуск и проверка результата",
          teaching:
            "Сразу после входа создай новый чат и отправь простой структурный запрос. Проверь, что ответ полезен, конкретен и без явных ошибок.",
          example:
            "Пример запроса: 'Роль: помощник преподавателя. Цель: план урока на 20 минут. Формат: 5 пунктов. Ограничение: простой язык'.",
          action: "Напиши, какой первый запрос отправишь после регистрации.",
          answerHint: "Шаблон: 'Роль: ... Цель: ... Формат: ... Ограничение: ...'",
          answerExample: "Роль: помощник по контенту. Цель: сделать структуру поста. Формат: 5 пунктов. Ограничение: без сложных терминов.",
          quizQuestion: "Что проверяем в первом ответе AI?",
          quizOptions: ["Только длину текста", "Пользу, конкретику и отсутствие грубых ошибок", "Ничего не проверяем"],
          quizCorrect: 1,
          quizExplain: "Верно: важна практическая применимость и качество.",
          mustInclude: ["роль", "цель", "формат"],
          lang,
        }),
      ],
      mission: {
        title: "Практика: регистрация и первый запрос",
        description:
          "Зарегистрируйся в AI-сервисе (или зайди в уже созданный), включи базовую безопасность, отправь первый структурный запрос и получи ответ. Приложи скриншот как подтверждение.",
        instructions: [
          "Зайди на сайт AI-сервиса и нажми 'Регистрация' / 'Sign up'.",
          "Подтверди почту и войди в аккаунт.",
          "Перейди в настройки и включи 2FA/двухфакторную авторизацию.",
          "Открой новый чат, отправь структурный запрос.",
          "Сделай скриншот результата и загрузи в миссию.",
        ],
        checkpoints: [
          "Виден AI-сервис и активная сессия",
          "Виден структурный запрос",
          "Виден ответ сервиса",
          "В комментарии описаны шаги безопасности",
        ],
        noteHint: "Опиши: где зарегистрировался, что включил по безопасности, какой запрос отправил.",
      },
    };
  }

  return {
    introScript:
      "Now we set up the basics correctly: pick services, register safely, and run your first practical request. At the end you upload screenshot proof.",
    steps: [
      makeStep({
        id: "acc-1",
        title: "Choose services by task",
        teaching: "Do not sign up for everything. Start with 1 text service and 1 visual service for your current goals.",
        example: "If you need writing and planning, begin with one text AI service.",
        action: "Write which 1-2 services you will use and for which tasks.",
        answerHint: "Template: 'I choose ... for ... and ... for ...'",
        answerExample: "I choose a text service for emails and plans, and an image service for lesson covers.",
        quizQuestion: "Best beginner setup?",
        quizOptions: ["Register in 10 services", "Start with 1-2 services for real tasks", "Pay for all tools first"],
        quizCorrect: 1,
        quizExplain: "Correct: start focused, then expand.",
        mustInclude: ["choose", "for", "tasks"],
        lang,
      }),
      makeStep({
        id: "acc-2",
        title: "Signup and security",
        teaching: "After signup, enable security immediately: strong password and two-factor authentication. Keep work access separate from personal.",
        example: "Checklist: work email, 2FA enabled, account recovery path saved.",
        action: "Describe two security steps you will apply right after signup.",
        answerHint: "Template: 'I will enable ... and ...'",
        answerExample: "I will enable a strong password and two-factor authentication.",
        quizQuestion: "What is mandatory after signup?",
        quizOptions: ["Only profile nickname", "2FA and strong password", "No setup needed"],
        quizCorrect: 1,
        quizExplain: "Correct: baseline security is mandatory.",
        mustInclude: ["enable", "password", "two"],
        lang,
      }),
      makeStep({
        id: "acc-3",
        title: "First run and quality check",
        teaching: "Open a new chat and send one structured request. Check output for usefulness, specificity, and obvious errors.",
        example: "Role: teaching assistant. Goal: 20-minute lesson plan. Format: 5 bullets. Constraint: plain language.",
        action: "Write your first structured request you will send.",
        answerHint: "Template: 'Role: ... Goal: ... Format: ... Constraint: ...'",
        answerExample: "Role: content assistant. Goal: post outline. Format: 5 bullets. Constraint: no jargon.",
        quizQuestion: "What do we verify in first AI output?",
        quizOptions: ["Only output length", "Usefulness, specificity, and major errors", "Nothing"],
        quizCorrect: 1,
        quizExplain: "Correct: practical usefulness and quality come first.",
        mustInclude: ["role", "goal", "format"],
        lang,
      }),
    ],
    mission: {
      title: "Practice: signup and first prompt",
      description:
        "Sign up (or log in), configure security basics, send your first structured prompt, and upload screenshot evidence.",
      instructions: [
        "Open AI service website and click Sign up.",
        "Verify email and log in.",
        "Open settings and enable 2FA.",
        "Start a new chat and send structured prompt.",
        "Take screenshot and upload it as evidence.",
      ],
      checkpoints: [
        "AI service interface is visible",
        "Structured prompt is visible",
        "Model output is visible",
        "Learner note includes security actions",
      ],
      noteHint: "Describe: where you signed up, what security setup you enabled, what prompt you used.",
    },
  };
}

function genericPreset(module, lang, profile) {
  const lessonLang = lang === "en" ? "en" : "ru";
  const sections = Array.isArray(module?.sections?.[lessonLang]) ? module.sections[lessonLang] : Array.isArray(module?.sections?.ru) ? module.sections.ru : [];
  const title = module?.title?.[lessonLang] || module?.title?.ru || module?.id || "module";
  const role = profile?.role || (lessonLang === "ru" ? "специалист" : "specialist");
  const summary = module?.summary?.[lessonLang] || module?.summary?.ru || "";

  if (lessonLang === "ru") {
    const stepTexts = sections.slice(0, 3);
    const mapped = stepTexts.map((text, idx) =>
      makeStep({
        id: `${module.id}-generic-${idx + 1}`,
        title: `Шаг ${idx + 1}: ключевая идея`,
        teaching: clip(text, 320),
        example: `Пример для роли ${role}: примени эту идею в одной рабочей задаче сегодня.`,
        action: "Опиши, как именно применишь этот шаг на своей задаче.",
        answerHint: "Шаблон: 'Для задачи ... я сделаю ... чтобы получить ...'",
        answerExample: "Для задачи подготовки урока я сделаю структурный запрос, чтобы получить понятный план занятия.",
        quizQuestion: "Как правильно пройти этот шаг?",
        quizOptions: ["Пропустить практику", "Сразу применить идею к реальной задаче", "Оставить без проверки"],
        quizCorrect: 1,
        quizExplain: "Верно: обучение закрепляется только через практику.",
        mustInclude: ["сделаю", "задача", "получить"],
        lang: lessonLang,
      })
    );

    return {
      introScript: `Модуль '${title}'. Кратко разберем теорию и сразу закрепим через практику на твоей задаче.`,
      steps: mapped,
      mission: {
        title: `Практика по модулю: ${title}`,
        description:
          "Выполни практику в AI-сервисе по теме модуля, получи результат и приложи скриншот, где видны запрос и ответ.",
        instructions: [
          "Открой AI-сервис и новый чат.",
          "Сформулируй запрос по теме текущего модуля.",
          "Получи ответ и проверь его по качеству.",
          "Сделай скриншот: запрос + результат.",
          "Загрузи скриншот и кратко опиши результат.",
        ],
        checkpoints: ["Виден запрос", "Виден ответ", "Комментарий: как применишь результат"],
        noteHint: "Опиши 2-3 предложениями, что сделал и какой результат получил.",
      },
    };
  }

  const stepTexts = sections.slice(0, 3);
  const mapped = stepTexts.map((text, idx) =>
    makeStep({
      id: `${module.id}-generic-${idx + 1}`,
      title: `Step ${idx + 1}: key idea`,
      teaching: clip(text, 320),
      example: `Example for role ${role}: apply this idea to one real task today.`,
      action: "Describe exactly how you will apply this step in your task.",
      answerHint: "Template: 'For task ... I will ... to get ...'",
      answerExample: "For lesson prep I will use a structured prompt to get a clear class plan.",
      quizQuestion: "What is the correct way to complete this step?",
      quizOptions: ["Skip practice", "Apply it to a real task immediately", "Leave it unchecked"],
      quizCorrect: 1,
      quizExplain: "Correct: learning sticks only with real practice.",
      mustInclude: ["will", "task", "result"],
      lang: lessonLang,
    })
  );

  return {
    introScript: `Module '${title}'. We keep theory short and apply everything immediately to your task.`,
    steps: mapped,
    mission: {
      title: `Practice mission: ${title}`,
      description: "Complete one AI task for this module and upload screenshot proof with prompt and output visible.",
      instructions: [
        "Open AI service and start new chat.",
        "Send module-related prompt.",
        "Review output quality.",
        "Take screenshot with prompt and output.",
        "Upload screenshot and add short note.",
      ],
      checkpoints: ["Prompt is visible", "Output is visible", "Learner note explains application"],
      noteHint: "Add 2-3 sentences about what you did and what result you got.",
    },
  };
}

export function buildLessonPlan(module, lang, profile) {
  if (!module) {
    return {
      introScript: "",
      steps: [],
      mission: {
        title: "",
        description: "",
        instructions: [],
        checkpoints: [],
        noteHint: "",
      },
    };
  }

  if (module.id === "foundation-ai-map") return lessonPresetAiMap(lang === "en" ? "en" : "ru");
  if (module.id === "foundation-account-setup") return lessonPresetAccountSetup(lang === "en" ? "en" : "ru");
  return genericPreset(module, lang, profile);
}

export function getModuleStepState(progress, moduleId) {
  if (!moduleId || !progress || typeof progress !== "object") return {};
  const raw = progress.steps?.[moduleId];
  if (!raw || typeof raw !== "object") return {};
  return raw;
}

export function countPassedSteps(progress, moduleId, totalSteps) {
  const state = getModuleStepState(progress, moduleId);
  const passed = Object.keys(state).filter((key) => state[key]).length;
  return Math.min(Math.max(0, passed), Math.max(0, totalSteps));
}

export function evaluateLearnerReply(step, reply, lang) {
  const text = (reply || "").trim();
  if (text.length < 30) {
    return {
      ok: false,
      feedback:
        lang === "ru"
          ? "Слишком коротко. Напиши 2-3 предложения: что понял и что конкретно сделаешь."
          : "Too short. Write 2-3 sentences: what you understood and what exact action you will take.",
      loseHeart: true,
    };
  }

  const normalized = text.toLowerCase();
  const hasAction = ACTION_VERBS[lang === "en" ? "en" : "ru"].test(normalized);
  const hasKeyword = Array.isArray(step?.keywords) && step.keywords.some((keyword) => normalized.includes(keyword));

  if (!hasAction || !hasKeyword) {
    return {
      ok: false,
      feedback:
        lang === "ru"
          ? "Добавь конкретику: ключевую мысль шага и действие ('сделаю/проверю/применю')."
          : "Add specificity: include one key idea and one concrete action ('I will apply/check/build').",
      loseHeart: true,
    };
  }

  return {
    ok: true,
    feedback: lang === "ru" ? "Отлично. Ответ засчитан." : "Great. Answer accepted.",
    loseHeart: false,
  };
}

export function evaluateStepQuiz(step, selectedIndex, lang) {
  if (!step?.quiz || !Array.isArray(step.quiz.options)) {
    return { ok: true, feedback: "" };
  }
  if (selectedIndex === null || selectedIndex === undefined) {
    return {
      ok: false,
      feedback: lang === "ru" ? "Выбери вариант ответа в мини-тесте." : "Choose an option in the mini quiz.",
    };
  }
  const correct = Number(step.quiz.correctIndex) === Number(selectedIndex);
  return {
    ok: correct,
    feedback: correct
      ? step.quiz.explain || (lang === "ru" ? "Верно." : "Correct.")
      : lang === "ru"
        ? "Пока неверно. Перечитай шаг и попробуй еще раз."
        : "Not correct yet. Re-read the step and try again.",
  };
}

function toIsoDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function applyStreakUpdate(progress) {
  const next = { ...(progress || {}) };
  const today = new Date();
  const todayIso = toIsoDate(today);
  const prevIso = typeof next.lastActiveDate === "string" ? next.lastActiveDate : "";

  if (prevIso === todayIso) return next;

  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  const yesterdayIso = toIsoDate(yesterday);

  const prevStreak = Number(next.streak || 0);
  next.streak = prevIso === yesterdayIso ? prevStreak + 1 : 1;
  next.lastActiveDate = todayIso;
  return next;
}
