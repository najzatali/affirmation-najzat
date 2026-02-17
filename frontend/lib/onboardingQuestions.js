export const areasCatalog = {
  ru: [
    { id: "money", title: "Деньги" },
    { id: "health", title: "Здоровье" },
    { id: "body", title: "Тело" },
    { id: "relationships", title: "Отношения" },
    { id: "career", title: "Карьера" },
    { id: "sleep", title: "Сон" },
  ],
  en: [
    { id: "money", title: "Money" },
    { id: "health", title: "Health" },
    { id: "body", title: "Body" },
    { id: "relationships", title: "Relationships" },
    { id: "career", title: "Career" },
    { id: "sleep", title: "Sleep" },
  ],
};

// Simplified interview: short path (about 10-12 questions for 3 areas).
export const onboardingQuestionBlocks = {
  ru: {
    perArea: [
      {
        key: "goal_real_desire",
        type: "text",
        text: "Какой реальный результат ты выбираешь в сфере {area}?",
        suggestions: [
          "Стабильный доход 500 000 рублей в месяц",
          "Сильное и выносливое тело с энергией каждый день",
          "Теплые отношения с уважением и близостью",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "Какие ощущения ты хочешь испытывать в сфере {area} ежедневно?",
        suggestions: [
          "Спокойствие, уверенность и легкость",
          "Ясность, фокус и внутренний баланс",
          "Радость, благодарность и стабильность",
        ],
      },
      {
        key: "reality_current",
        type: "text",
        text: "Какое действие ты готов делать регулярно в сфере {area}?",
        suggestions: [
          "Держать фокус на 3 главных шагах каждый день",
          "Регулярно тренироваться и восстанавливаться",
          "Планировать и выполнять ключевые задачи без суеты",
        ],
      },
    ],
    global: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Какая мысль чаще всего мешала результату раньше?",
        suggestions: [
          "Я думал, что мне не хватит дисциплины",
          "Я считал, что это слишком сложно",
          "Я боялся ошибиться и потерять время",
        ],
      },
      {
        key: "faith_possible",
        type: "scale",
        min: 1,
        max: 10,
        text: "Насколько ты веришь, что это возможно? (1-10)",
      },
      {
        key: "faith_worthy",
        type: "scale",
        min: 1,
        max: 10,
        text: "Насколько ты считаешь себя достойным этого результата? (1-10)",
      },
    ],
  },
  en: {
    perArea: [
      {
        key: "goal_real_desire",
        type: "text",
        text: "What real result do you choose in {area}?",
        suggestions: [
          "Stable monthly income with confidence",
          "Strong resilient body with daily energy",
          "Warm relationships with respect and closeness",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "What feelings do you want to experience in {area} every day?",
        suggestions: [
          "Calm, confidence, and lightness",
          "Clarity, focus, and inner balance",
          "Joy, gratitude, and stability",
        ],
      },
      {
        key: "reality_current",
        type: "text",
        text: "Which regular action are you ready to do in {area}?",
        suggestions: [
          "Focus on top 3 actions every day",
          "Train and recover consistently",
          "Plan and execute key tasks with calm discipline",
        ],
      },
    ],
    global: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Which thought blocked your result before?",
        suggestions: [
          "I thought I lacked discipline",
          "I believed it was too difficult",
          "I was afraid of making mistakes",
        ],
      },
      {
        key: "faith_possible",
        type: "scale",
        min: 1,
        max: 10,
        text: "How much do you believe this is possible? (1-10)",
      },
      {
        key: "faith_worthy",
        type: "scale",
        min: 1,
        max: 10,
        text: "How worthy do you feel of this result? (1-10)",
      },
    ],
  },
};
