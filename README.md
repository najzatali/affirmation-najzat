# AIMPACT Academy

Adaptive AI learning platform with personalized learning paths for individuals and corporate teams.

## What is implemented

- Personalized onboarding by age group, industry, role, goals, level, and learning format.
- Adaptive module path generator (text + voice mode support).
- Gamified lesson player with XP, quest tracking, and progress persistence.
- Corporate pricing tiers:
  - up to 5 employees: 10,000 RUB
  - up to 10 employees: 20,000 RUB
  - up to 50 employees: 30,000 RUB
  - up to 100 employees: 50,000 RUB
- Individual package: 2,990 RUB (one-time payment).
- Training checkout API with Robokassa support.

## Quick start

1. Copy env files:
   - `cp backend/.env.example backend/.env`
   - `cp worker/.env.example worker/.env`
   - `cp frontend/.env.example frontend/.env`
2. Run stack:
   - `docker compose up --build`
3. Open:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Robokassa setup

Set in `backend/.env`:

```env
BILLING_PROVIDER=robokassa
ROBOKASSA_LOGIN=your_login
ROBOKASSA_PASSWORD_1=your_password_1
ROBOKASSA_PASSWORD_2=your_password_2
ROBOKASSA_TEST_MODE=true
ROBOKASSA_CHECKOUT_URL=https://auth.robokassa.ru/Merchant/Index.aspx
```

Use webhook URL in Robokassa cabinet:

- Result URL: `https://<your-domain>/api/webhooks/robokassa/result`

## Key API endpoints

- `GET /api/billing/training-plans`
- `GET /api/billing/training-orders`
- `POST /api/billing/training-orders`
- `POST /api/webhooks/robokassa/result`

## Frontend pages

- `/` — marketing landing + ROI calculator
- `/onboarding` — personalization profile
- `/library` — adaptive module path
- `/record` — lesson player (text/voice)
- `/billing` — individual/corporate checkout
