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

export const questionBlockOrder = ["goal", "reality", "beliefs", "faith"];

export const onboardingQuestionBlocks = {
  ru: {
    goal: [
      {
        key: "goal_real_desire",
        type: "text",
        text: "Чего ты хочешь на самом деле в сфере {area}?",
        suggestions: [
          "Стабильный доход 500 000 рублей в месяц",
          "Сильное, выносливое и энергичное тело",
          "Гармоничные отношения с уважением и теплом",
        ],
      },
      {
        key: "goal_why",
        type: "text",
        text: "Почему это важно для тебя лично?",
        suggestions: [
          "Это дает свободу, безопасность и спокойствие",
          "Это усиливает уважение к себе и уверенность",
          "Это улучшает качество моей жизни и отношений",
        ],
      },
      {
        key: "goal_life_change",
        type: "text",
        text: "Как изменится твоя жизнь, когда это станет нормой?",
        suggestions: [
          "Я стану более спокойным и собранным каждый день",
          "Я буду принимать зрелые решения без суеты",
          "Я начну больше времени уделять семье и развитию",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "Какие чувства ты хочешь испытывать ежедневно?",
        suggestions: [
          "Ясность, уверенность и легкость",
          "Вдохновение, благодарность и внутренний баланс",
          "Силу, спокойствие и радость",
        ],
      },
    ],
    reality: [
      {
        key: "reality_current",
        type: "text",
        text: "Что сейчас происходит в этой сфере?",
        suggestions: [
          "Действую нестабильно и быстро теряю фокус",
          "Есть прогресс, но не хватает регулярности",
          "Часто переключаюсь и откладываю важные шаги",
        ],
      },
      {
        key: "reality_pain",
        type: "text",
        text: "Что тебя беспокоит сильнее всего?",
        suggestions: [
          "Нестабильный результат и тревога",
          "Переутомление и потеря энергии",
          "Ощущение, что я двигаюсь медленно",
        ],
      },
      {
        key: "reality_fear",
        type: "text",
        text: "Где чаще всего появляется зажим или страх?",
        suggestions: [
          "Когда нужно принять важное решение",
          "Когда нужно заявить о себе и своих границах",
          "Когда нужно взять большую ответственность",
        ],
      },
      {
        key: "reality_pattern",
        type: "text",
        text: "Какая ситуация повторяется снова и снова?",
        suggestions: [
          "Откладываю важные действия до последнего",
          "Сомневаюсь и откатываюсь назад",
          "Ставлю цели, но не довожу до системы",
        ],
      },
    ],
    beliefs: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Почему, как тебе кажется, этого результата еще нет?",
        suggestions: [
          "Я думал, что мне не хватает дисциплины",
          "Я считал, что это слишком сложно для меня",
          "Я боялся ошибиться и потерять время",
        ],
      },
      {
        key: "belief_self_view",
        type: "text",
        text: "Что ты думаешь о себе в этой сфере?",
        suggestions: [
          "Я человек, который учится действовать уверенно",
          "Я усиливаю внутреннюю опору и зрелость",
          "Я становлюсь стабильным и системным",
        ],
      },
      {
        key: "belief_childhood",
        type: "text",
        text: "Что ты слышал в детстве по этой теме?",
        suggestions: [
          "Деньги приходят тяжело",
          "Нужно быть идеальным, чтобы тебя ценили",
          "Лучше не выделяться",
        ],
      },
      {
        key: "belief_auto_thought",
        type: "text",
        text: "Какая мысль возникает первой, когда думаешь о цели?",
        suggestions: [
          "Справлюсь и соберу это по шагам",
          "Мне важно действовать спокойно и последовательно",
          "У меня уже есть база для роста",
        ],
      },
    ],
    faith: [
      { key: "faith_possible", type: "scale", min: 1, max: 10, text: "Насколько ты веришь, что это возможно? (1-10)" },
      { key: "faith_worthy", type: "scale", min: 1, max: 10, text: "Насколько ты считаешь себя достойным этого? (1-10)" },
    ],
  },
  en: {
    goal: [
      {
        key: "goal_real_desire",
        type: "text",
        text: "What do you truly want in {area}?",
        suggestions: [
          "Stable monthly income and financial confidence",
          "A strong energetic body with consistent habits",
          "Warm and respectful relationships",
        ],
      },
      {
        key: "goal_why",
        type: "text",
        text: "Why is it personally important for you?",
        suggestions: [
          "It gives me freedom, safety, and calm",
          "It strengthens my self-respect",
          "It improves the quality of my life",
        ],
      },
      {
        key: "goal_life_change",
        type: "text",
        text: "How will your life change when this becomes normal?",
        suggestions: [
          "I will feel steady and focused every day",
          "I will make mature decisions calmly",
          "I will have more time for family and growth",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "What feelings do you want to experience daily?",
        suggestions: [
          "Clarity, confidence, and lightness",
          "Inspiration, gratitude, and balance",
          "Strength, calm, and joy",
        ],
      },
    ],
    reality: [
      {
        key: "reality_current",
        type: "text",
        text: "What is happening now in this area?",
        suggestions: [
          "My actions are inconsistent",
          "I have progress but lack consistency",
          "I postpone key steps too often",
        ],
      },
      {
        key: "reality_pain",
        type: "text",
        text: "What concerns you the most right now?",
        suggestions: [
          "Unstable results and inner tension",
          "Low energy and overload",
          "Feeling of moving too slowly",
        ],
      },
      {
        key: "reality_fear",
        type: "text",
        text: "Where do you feel fear or tension most often?",
        suggestions: [
          "When I need to make an important decision",
          "When I need to set clear boundaries",
          "When I step into bigger responsibility",
        ],
      },
      {
        key: "reality_pattern",
        type: "text",
        text: "Which situation keeps repeating?",
        suggestions: [
          "I delay important actions",
          "I doubt myself and roll back",
          "I set goals but lose the system",
        ],
      },
    ],
    beliefs: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Why do you think this result is not here yet?",
        suggestions: [
          "I thought I lacked discipline",
          "I thought it was too hard for me",
          "I was afraid of mistakes",
        ],
      },
      {
        key: "belief_self_view",
        type: "text",
        text: "How do you see yourself in this area?",
        suggestions: [
          "I am learning to act with confidence",
          "I am building inner stability",
          "I am becoming consistent and reliable",
        ],
      },
      {
        key: "belief_childhood",
        type: "text",
        text: "What did you hear in childhood about this topic?",
        suggestions: [
          "Money is always difficult",
          "You must be perfect to be valued",
          "It is safer not to stand out",
        ],
      },
      {
        key: "belief_auto_thought",
        type: "text",
        text: "What is your first automatic thought about your goal?",
        suggestions: [
          "I can build this step by step",
          "I move calmly and consistently",
          "I already have a strong base to grow",
        ],
      },
    ],
    faith: [
      { key: "faith_possible", type: "scale", min: 1, max: 10, text: "How much do you believe this is possible? (1-10)" },
      { key: "faith_worthy", type: "scale", min: 1, max: 10, text: "How worthy do you feel of this result? (1-10)" },
    ],
  },
};
