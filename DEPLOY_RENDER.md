# Deploying MatchColab to Render

This guide sets up your Node/Express API on Render. It uses the included `render.yaml` and your existing backend at `backend/`.

## Prerequisites
- A GitHub repo with this project
- Render account (free plan is fine)
- Rotated secrets (don’t use the committed `.env` values)

## 1) Prepare environment variables
In Render, create a Web Service and add these environment variables:
- OPENAI_API_KEY: your OpenAI key
- SUPABASE_URL: your Supabase project URL
- SUPABASE_SERVICE_KEY: service role key (keep private; do not expose to frontend)
- CORS_ORIGIN: comma-separated allowlist of frontend origins (e.g., `https://your-frontend.onrender.com,https://yourdomain.com`). Leave blank for permissive dev.

Render automatically injects PORT; the app already reads `process.env.PORT`.

## 2) One‑click via render.yaml
We include `render.yaml` at the repo root. On Render:
- New + → Blueprint → Connect your GitHub repo
- Render will read `render.yaml` and create the service:
  - Type: Web
  - Runtime: Node
  - Root directory: `backend`
  - Build: `npm install`
  - Start: `node server.js`
  - Health check: `/health`

Alternatively, create a Web Service manually and point to the `backend` folder, setting the same commands.

## 3) Health checks
The server exposes:
- GET `/health` → `{ "status": "ok" }`
Use this path in Render health checks (already configured in `render.yaml`).

## 4) CORS
CORS is configured to allow all origins by default if `CORS_ORIGIN` is not set. In production, set `CORS_ORIGIN` as a comma‑separated list of allowed origins so the browser can call your API:
```
CORS_ORIGIN=https://your-frontend.onrender.com,https://yourdomain.com
```

## 5) Logs and debugging
- View logs in Render Dashboard → your service → Logs
- If startup fails, verify environment variables and that the app binds to `PORT`.

## 6) Security notes
- Do not commit secrets. Add `.env` to `.gitignore` (this repo includes one—rotate and remove it from history if needed).
- The `SUPABASE_SERVICE_KEY` is sensitive; keep it server‑side only.

## 7) Local development
From `backend/`:
```powershell
npm install
npx nodemon server.js
# or
node server.js
```
Test locally:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
$body = '{"tags":"lofi, chill","top_n":5}'
Invoke-RestMethod -Uri "http://localhost:5000/match" -Method Post -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 6
```

## 8) Frontend (later)
- You can deploy a static site on Render as a separate Static Site service, or any other host.
- Point your frontend to the API URL Render provides (e.g., `https://matchcolab-api.onrender.com`).
- Ensure that origin is in `CORS_ORIGIN`.

## 9) Troubleshooting
- 500 on `/match`: Make sure the Supabase SQL function `rank_artists_by_embedding` exists (apply `supabase_functions.sql` in Supabase SQL Editor).
- CORS error in browser: Add your frontend origin to `CORS_ORIGIN`.
- Empty matches: Lower `min_similarity` or verify embeddings stored for artists.
- Invalid OpenAI key: Rotate in Render env vars and redeploy.

That’s it—deploys will auto‑run on each push to `main` if you leave Auto‑Deploy enabled in Render.
