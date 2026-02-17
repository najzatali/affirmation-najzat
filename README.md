# Affirmation Studio

Production-style SaaS MVP for personal affirmations:
- Guided onboarding by life areas (RU/EN)
- AI text generation in **"Я есть / Я имею"** format
- Voice sample upload with consent
- System voice selection (3 female + 3 male) with preview
- Background music selection with preview
- Async audio generation in queue (worker)
- MP3 download and library history
- Pricing packs: 30 sec demo, 2-5 min paid durations

---

## 1) Run on GitHub domain (recommended)

This is the easiest way to test without localhost conflicts.

### Step A. Open Codespaces
1. Open your repo: `https://github.com/najzatali/affirmation-najzat`
2. Click **Code** -> **Codespaces** -> **Create codespace on main**
3. Wait until web VS Code opens

### Step B. Start project
In Codespaces terminal run:

```bash
cp backend/.env.example backend/.env
cp worker/.env.example worker/.env
cp frontend/.env.example frontend/.env
docker compose up -d --build
```

### Step C. Open app
1. Open tab **Ports**
2. For port **3000** click **Open in Browser**
3. You will get URL like: `https://...-3000.app.github.dev`

That is your GitHub domain for testing.

---

## 2) Local run (Mac)

```bash
cd "/Users/najzat/Documents/affirmation-najzat"
cp backend/.env.example backend/.env
cp worker/.env.example worker/.env
cp frontend/.env.example frontend/.env
docker compose up -d --build
```

Open:
- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

---

## 3) If you run 2 projects at once

Use another port set for this project:

```bash
cd "/Users/najzat/Documents/affirmation-najzat"
FRONTEND_PORT=4000 BACKEND_PORT=8100 MINIO_PORT=9100 MINIO_CONSOLE_PORT=9101 docker compose -p affirmation up -d --build
```

Open:
- Frontend: `http://localhost:4000`
- Backend: `http://localhost:8100/docs`

Stop only this project:

```bash
docker compose -p affirmation down
```

---

## 4) Required API keys (optional for MVP)

MVP works without paid keys, but quality is better with keys.

### LLM (text quality)
- Recommended: DeepSeek
- Put in `backend/.env`:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key
```

### TTS (voice quality)
- Recommended for RU/CIS: Yandex SpeechKit
- Put in `worker/.env`:

```env
TTS_PROVIDER=yandex
YANDEX_API_KEY=your_key
```

Without keys, app falls back to free providers.

---

## 5) Core user flow to test

1. Open `/onboarding`
2. Select 1-3 areas
3. Answer all guided questions
4. Click **Generate affirmations**
5. Click **Convert to voice**
6. On `/record`:
   - Choose voice mode (system or my voice)
   - If my voice: record -> listen -> upload (with consent)
   - Choose music
   - Choose duration (30s demo or paid pack)
   - Generate audio
7. Download MP3

---

## 6) Pricing model in MVP

- Demo: **30 sec free**
- 2 min: **190 RUB**
- 3 min: **290 RUB**
- 4 min: **390 RUB**
- 5 min: **450 RUB**

In `BILLING_PROVIDER=local`, package is activated instantly for testing.

---

## 7) Privacy and legal notes implemented

- Voice upload requires consent checkbox
- User can delete voice data (`DELETE /api/privacy/voice`)
- Audio can be deleted after download
- Retention cleanup endpoint (`POST /api/privacy/cleanup`)
- UI includes AI transparency + non-medical disclaimer

---

## 8) Useful commands

### Logs
```bash
docker compose logs --tail=100 frontend backend worker
```

### Smoke tests
```bash
docker compose exec -T backend pytest -q
```

### Rebuild cleanly
```bash
docker compose down
docker compose up -d --build
```

---

## 9) Deploy after MVP (next)

Recommended production setup:
1. Frontend -> Vercel
2. Backend + Worker + Postgres + Redis + S3 -> Render / Fly / AWS
3. Stripe webhooks for real checkout
4. Real auth (magic link/OAuth) instead of demo-user
