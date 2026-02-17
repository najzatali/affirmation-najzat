export const corporateTiers = [
  {
    id: "team_5",
    maxSeats: 5,
    priceRub: 10000,
    label: { ru: "До 5 сотрудников", en: "Up to 5 employees" },
  },
  {
    id: "team_10",
    maxSeats: 10,
    priceRub: 20000,
    label: { ru: "До 10 сотрудников", en: "Up to 10 employees" },
  },
  {
    id: "team_50",
    maxSeats: 50,
    priceRub: 30000,
    label: { ru: "До 50 сотрудников", en: "Up to 50 employees" },
  },
  {
    id: "team_100",
    maxSeats: 100,
    priceRub: 50000,
    label: { ru: "До 100 сотрудников", en: "Up to 100 employees" },
  },
];

export function getTierForSeats(seats) {
  const n = Number(seats || 0);
  if (n <= 0) return corporateTiers[0];
  return corporateTiers.find((tier) => n <= tier.maxSeats) || corporateTiers[corporateTiers.length - 1];
}

export function formatRub(value, locale = "ru-RU") {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}
