export const onboardingQuestionBlocks = {
  ru: {
    goal: [
      {
        key: "goal_real_desire",
        type: "text",
        text: "Какой конкретный результат ты выбираешь в сфере {area}?",
        suggestions: [
          "Стабильный доход 500 000 рублей в месяц без выгорания",
          "Сильное и энергичное тело с регулярными тренировками",
          "Теплые отношения с уважением и поддержкой каждый день",
        ],
      },
      {
        key: "goal_why",
        type: "text",
        text: "Почему это важно для тебя лично?",
        suggestions: [
          "Это дает мне свободу, спокойствие и уверенность за семью",
          "Это усиливает мое уважение к себе и моим решениям",
          "Это помогает мне жить в балансе и фокусе",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "Какие чувства ты выбираешь испытывать в этой сфере ежедневно?",
        suggestions: [
          "Уверенность, легкость и внутреннюю силу",
          "Спокойствие, ясность и благодарность",
          "Радость, вдохновение и устойчивость",
        ],
      },
    ],
    reality: [
      {
        key: "reality_current",
        type: "text",
        text: "Какие действия ты уже готов делать регулярно?",
        suggestions: [
          "Планировать день и держать фокус на трех приоритетах",
          "Делать прогулку и короткую тренировку каждый день",
          "Вести учет расходов и доходов ежедневно",
        ],
      },
      {
        key: "reality_pattern",
        type: "text",
        text: "Какой повторяющийся сценарий ты закрываешь сейчас?",
        suggestions: [
          "Откладывание важных действий до последнего",
          "Потеря фокуса из-за лишних задач и тревоги",
          "Эмоциональные решения вместо спокойной стратегии",
        ],
      },
      {
        key: "reality_fear",
        type: "text",
        text: "В какой ситуации тебе чаще всего не хватает уверенности?",
        suggestions: [
          "Когда нужно принимать финансовые решения",
          "Когда нужно отстаивать границы в общении",
          "Когда нужно выходить в новые проекты и ответственность",
        ],
      },
    ],
    beliefs: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Какая мысль мешала результату раньше?",
        suggestions: [
          "Что мне нужно быть идеальным, чтобы иметь результат",
          "Что большие цели слишком сложны для меня",
          "Что я не всегда довожу дела до конца",
        ],
      },
      {
        key: "belief_self_view",
        type: "text",
        text: "Какой новый образ себя ты выбираешь вместо старого?",
        suggestions: [
          "Я дисциплинированный и надежный человек",
          "Я уверен в себе и спокойно принимаю решения",
          "Я человек, который стабильно растет и укрепляет результат",
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
        text: "What concrete result do you choose in {area}?",
        suggestions: [
          "Steady income of 5000 USD per month without burnout",
          "A strong energetic body with consistent workouts",
          "Warm relationships with daily respect and support",
        ],
      },
      {
        key: "goal_why",
        type: "text",
        text: "Why does this matter to you personally?",
        suggestions: [
          "It gives me freedom, calm, and confidence for my family",
          "It strengthens my self-respect and decisions",
          "It helps me live with balance and focus",
        ],
      },
      {
        key: "goal_feeling",
        type: "text",
        text: "What feelings do you choose to experience daily in this area?",
        suggestions: [
          "Confidence, lightness, and inner strength",
          "Calm, clarity, and gratitude",
          "Joy, inspiration, and stability",
        ],
      },
    ],
    reality: [
      {
        key: "reality_current",
        type: "text",
        text: "Which actions are you ready to do consistently?",
        suggestions: [
          "Plan my day and focus on top three priorities",
          "Take a walk and do a short workout daily",
          "Track income and expenses every day",
        ],
      },
      {
        key: "reality_pattern",
        type: "text",
        text: "Which repeating pattern are you closing now?",
        suggestions: [
          "Delaying key actions until the last moment",
          "Losing focus because of too many low-value tasks",
          "Emotional decisions instead of calm strategy",
        ],
      },
      {
        key: "reality_fear",
        type: "text",
        text: "In which situations do you most lack confidence?",
        suggestions: [
          "When making financial decisions",
          "When I need to set boundaries in communication",
          "When I step into bigger projects and responsibility",
        ],
      },
    ],
    beliefs: [
      {
        key: "belief_why_not",
        type: "text",
        text: "Which thought blocked results before?",
        suggestions: [
          "I must be perfect before I can succeed",
          "Big goals are too difficult for me",
          "I do not always finish what I start",
        ],
      },
      {
        key: "belief_self_view",
        type: "text",
        text: "Which new identity do you choose instead?",
        suggestions: [
          "I am disciplined and reliable",
          "I am confident and calm in decisions",
          "I am a person who grows steadily and keeps momentum",
        ],
      },
    ],
    faith: [
      { key: "faith_possible", type: "scale", min: 1, max: 10, text: "How much do you believe this is possible? (1-10)" },
      { key: "faith_worthy", type: "scale", min: 1, max: 10, text: "How worthy do you feel of this result? (1-10)" },
    ],
  },
};

export const questionBlockOrder = ["goal", "reality", "beliefs", "faith"];
