export const diagnosticInterview = {
  ru: [
    {
      id: "ai_frequency",
      prompt: "Как часто ты уже используешь AI в повседневных задачах?",
      options: [
        { value: 0, label: "Почти не использую", coach: "Отлично, начнем с базовой логики и безопасного старта." },
        { value: 1, label: "1-2 раза в неделю", coach: "Хорошая база. Покажу, как перейти к системному использованию." },
        { value: 2, label: "Каждый день, но хаотично", coach: "Сфокусируемся на структурных промптах и шаблонах." },
        { value: 3, label: "Каждый день по четкому процессу", coach: "Сделаем упор на автоматизацию и качество на уровне команды." },
      ],
    },
    {
      id: "prompt_skill",
      prompt: "Насколько уверенно ты пишешь промпты с ограничениями и форматом результата?",
      options: [
        { value: 0, label: "Пока не умею", coach: "Добавлю тренировочный блок по промпт-инженерии с примерами." },
        { value: 1, label: "Иногда получается", coach: "Усилим структуру запроса и контроль качества ответа." },
        { value: 2, label: "Обычно получается", coach: "Переходим к продвинутым шаблонам под роли." },
        { value: 3, label: "Уверенно пишу сложные промпты", coach: "Сделаю упор на оптимизацию и масштабирование в процессах." },
      ],
    },
    {
      id: "fact_check",
      prompt: "Как ты проверяешь факты и цифры в ответах AI?",
      options: [
        { value: 0, label: "Почти не проверяю", coach: "Обязательно добавим строгий модуль факт-чекинга." },
        { value: 1, label: "Проверяю выборочно", coach: "Дадим чеклист перед каждым рабочим результатом." },
        { value: 2, label: "Проверяю важные данные", coach: "Усилим системность и прозрачность проверок." },
        { value: 3, label: "У меня есть четкий протокол", coach: "Отлично, перейдем к автоматизации контроля качества." },
      ],
    },
    {
      id: "tool_stack",
      prompt: "С какими типами AI-инструментов ты работаешь?",
      options: [
        { value: 0, label: "Только текст", coach: "Построим плавный переход к изображениям и видео." },
        { value: 1, label: "Текст + иногда картинки", coach: "Добавим практику по мультимодальным связкам." },
        { value: 2, label: "Текст + картинки + видео", coach: "Сконцентрируемся на качестве и скорости продакшна." },
        { value: 3, label: "Широкий стек + автоматизации", coach: "Пойдем в продвинутую оркестрацию и playbooks." },
      ],
    },
    {
      id: "tools_used",
      prompt: "Какие AI-сервисы ты уже реально использовал?",
      options: [
        { value: 0, label: "Почти никакие", coach: "Начнем с карты базовых AI-инструментов и где какой нужен." },
        { value: 1, label: "Только 1 сервис", coach: "Расширим стек до текста, изображений и видео по задачам." },
        { value: 2, label: "2-3 сервиса", coach: "Соберем рабочий набор и правила выбора сервиса под кейс." },
        { value: 3, label: "4+ сервисов", coach: "Сфокусируемся на оркестрации и едином рабочем стандарте." },
      ],
    },
    {
      id: "account_setup",
      prompt: "Насколько уверенно ты умеешь регистрироваться и настраивать аккаунты в AI-сервисах?",
      options: [
        { value: 0, label: "Не умею / нужна пошаговая помощь", coach: "Добавлю максимально простой старт: регистрация, вход и первые настройки." },
        { value: 1, label: "Иногда получается", coach: "Дадим понятный чеклист, чтобы не терять доступы и настройки." },
        { value: 2, label: "Обычно справляюсь", coach: "Усилим практику по безопасной настройке и рабочим шаблонам." },
        { value: 3, label: "Уверенно настраиваю", coach: "Сфокусируемся на оптимизации и мультисервисной работе." },
      ],
    },
    {
      id: "payments_skill",
      prompt: "Насколько уверенно ты понимаешь оплату AI-сервисов и доступов (особенно для команды)?",
      options: [
        { value: 0, label: "Не понимаю совсем", coach: "Добавлю базовый модуль: как оплачивать и как не потерять доступы." },
        { value: 1, label: "Примерно понимаю", coach: "Уточним схему оплаты, роли ответственных и лимиты расходов." },
        { value: 2, label: "Понимаю для себя", coach: "Переходим к корпоративной схеме: бюджеты, доступы, контроль." },
        { value: 3, label: "Уверенно управляю", coach: "Дадим продвинутые практики управления рисками и KPI внедрения." },
      ],
    },
    {
      id: "business_goal",
      prompt: "Какая главная цель от обучения прямо сейчас?",
      options: [
        { value: 0, label: "Разобраться с нуля", coach: "Соберу маршрут с мягким входом и пошаговой практикой." },
        { value: 1, label: "Ускорить личную работу", coach: "Дадим быстрые сценарии экономии времени." },
        { value: 2, label: "Улучшить качество результата", coach: "Добавлю больше модулей по контролю качества." },
        { value: 3, label: "Внедрить AI в команду", coach: "Сфокусируемся на корпоративных процессах и ролях." },
      ],
    },
    {
      id: "team_readiness",
      prompt: "Если это обучение для команды: насколько сотрудники готовы к AI?",
      options: [
        { value: 0, label: "Не готовы", coach: "Маршрут начнется с общего уровня AI-грамотности." },
        { value: 1, label: "Есть единичные пользователи", coach: "Сделаем единый стандарт использования для всех." },
        { value: 2, label: "Половина уже использует", coach: "Пойдем через ролевые кейсы и метрики." },
        { value: 3, label: "Большинство уже в процессе", coach: "Добавим продвинутую часть: governance и контроль качества." },
      ],
    },
  ],
  en: [
    {
      id: "ai_frequency",
      prompt: "How often do you already use AI in daily work?",
      options: [
        { value: 0, label: "Almost never", coach: "Great, we will start with fundamentals and safe setup." },
        { value: 1, label: "1-2 times per week", coach: "Good baseline. We will move to systematic usage." },
        { value: 2, label: "Daily, but chaotic", coach: "We will focus on structured prompts and templates." },
        { value: 3, label: "Daily with clear process", coach: "We will focus on automation and team-grade quality." },
      ],
    },
    {
      id: "prompt_skill",
      prompt: "How confident are you with prompts that include constraints and output formats?",
      options: [
        { value: 0, label: "I cannot do this yet", coach: "We will add a clear prompt engineering training block." },
        { value: 1, label: "It works sometimes", coach: "We will strengthen request structure and quality control." },
        { value: 2, label: "Usually works", coach: "We can move to advanced role-specific templates." },
        { value: 3, label: "I handle complex prompts", coach: "We will prioritize optimization and scaling workflows." },
      ],
    },
    {
      id: "fact_check",
      prompt: "How do you verify facts and numbers in AI outputs?",
      options: [
        { value: 0, label: "I rarely verify", coach: "We will include strict fact-checking modules first." },
        { value: 1, label: "I verify occasionally", coach: "We will enforce a practical pre-delivery checklist." },
        { value: 2, label: "I verify important data", coach: "We will improve consistency and transparency." },
        { value: 3, label: "I have a strict protocol", coach: "Great, then we focus on automated quality control." },
      ],
    },
    {
      id: "tool_stack",
      prompt: "What AI modalities do you currently use?",
      options: [
        { value: 0, label: "Text only", coach: "We will gradually add image and video workflows." },
        { value: 1, label: "Text + occasional image", coach: "We will build multi-modal production flow." },
        { value: 2, label: "Text + image + video", coach: "We will focus on speed and quality at scale." },
        { value: 3, label: "Full stack + automations", coach: "We will move to orchestration and playbooks." },
      ],
    },
    {
      id: "tools_used",
      prompt: "Which AI services have you actually used before?",
      options: [
        { value: 0, label: "Almost none", coach: "We will start from AI tool map and practical use-cases." },
        { value: 1, label: "Only one service", coach: "We will expand to text, image, and video workflows." },
        { value: 2, label: "2-3 services", coach: "We will build a practical stack and service selection rules." },
        { value: 3, label: "4+ services", coach: "We will focus on orchestration and unified workflow standards." },
      ],
    },
    {
      id: "account_setup",
      prompt: "How confident are you with registering and configuring AI service accounts?",
      options: [
        { value: 0, label: "Not confident, need step-by-step", coach: "We will add a simple onboarding block: signup, access, and first settings." },
        { value: 1, label: "Sometimes I manage", coach: "We will provide a reliable setup checklist to avoid access issues." },
        { value: 2, label: "Usually confident", coach: "We will reinforce secure setup practices and reusable templates." },
        { value: 3, label: "Fully confident", coach: "We will focus on optimization across multiple services." },
      ],
    },
    {
      id: "payments_skill",
      prompt: "How confident are you with AI service payments and access setup (especially for teams)?",
      options: [
        { value: 0, label: "Not confident at all", coach: "We will include a basic module on payments and access control." },
        { value: 1, label: "Partially confident", coach: "We will clarify payment flow, ownership, and spend limits." },
        { value: 2, label: "Confident for individual use", coach: "We will extend this to company-grade setup and control." },
        { value: 3, label: "Fully confident", coach: "We will add advanced governance and KPI-based management." },
      ],
    },
    {
      id: "business_goal",
      prompt: "What is your immediate goal from this training?",
      options: [
        { value: 0, label: "Understand from scratch", coach: "Your path will start with guided fundamentals." },
        { value: 1, label: "Speed up my work", coach: "We will prioritize quick productivity scenarios." },
        { value: 2, label: "Improve output quality", coach: "We will add more quality-control modules." },
        { value: 3, label: "Deploy AI for team", coach: "We will focus on role-based team implementation." },
      ],
    },
    {
      id: "team_readiness",
      prompt: "If this is for a team: how ready are employees for AI workflows?",
      options: [
        { value: 0, label: "Not ready", coach: "We start with shared AI literacy baseline." },
        { value: 1, label: "Only a few users", coach: "We create a common usage standard." },
        { value: 2, label: "About half already use it", coach: "We move through role-based practical cases." },
        { value: 3, label: "Most already use it", coach: "We add advanced governance and quality layers." },
      ],
    },
  ],
};

export function evaluateDiagnostic(lang, answers) {
  const questions = diagnosticInterview[lang] || diagnosticInterview.ru;
  const maxScore = questions.length * 3;

  const rawScore = questions.reduce((sum, item) => {
    const value = Number(answers[item.id] ?? 0);
    return sum + Math.min(3, Math.max(0, value));
  }, 0);

  const scorePercent = maxScore > 0 ? Math.round((rawScore / maxScore) * 100) : 0;
  let levelId = "beginner";
  let levelLabel = lang === "ru" ? "Новичок" : "Beginner";
  let startModuleId = "foundation-ai-map";

  if (scorePercent >= 80) {
    levelId = "advanced";
    levelLabel = lang === "ru" ? "Продвинутый" : "Advanced";
    startModuleId = "foundation-prompt-iteration";
  } else if (scorePercent >= 55) {
    levelId = "intermediate";
    levelLabel = lang === "ru" ? "Средний" : "Intermediate";
    startModuleId = "foundation-ai-map";
  }

  const summary =
    lang === "ru"
      ? `Диагностика завершена: ${scorePercent}% готовности. Рекомендуемый стартовый уровень — ${levelLabel}.`
      : `Diagnostic complete: ${scorePercent}% readiness. Recommended starting level — ${levelLabel}.`;

  return {
    scorePercent,
    levelId,
    levelLabel,
    startModuleId,
    summary,
  };
}
