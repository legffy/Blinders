# Blinders

Blinders is a browser extension + web app that helps users reduce impulsive browsing by identifying “high-dopamine” websites and adding small friction (delay walls, reflections) before opening them. The goal is simple: put guardrails on distractions and boost intentionality online.

Tech stack: Next.js (React + TypeScript) · FastAPI (Python) · Postgres (Supabase/Neon) · Chrome MV3 Extension

🧠 Project Structure
/api         → FastAPI backend (REST API, auth, DB models)
/web         → Next.js frontend (dashboard & settings)
/extension   → Chrome MV3 extension (delay wall, domain detection)
/infra       → Deployment config, docker, CI files

⚙️ Local Setup
1️⃣ Clone the Repo
git clone https://github.com/<your-username>/blinders.git
cd blinders

2️⃣ Backend (FastAPI)
Install dependencies
cd api
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt

Add environment variables

Create a .env file in /api:

DATABASE_URL=your_postgres_url_here
JWT_SECRET=your_secret_key_here

Run the backend
uvicorn main:app --reload


API will be live at:
http://localhost:8000

Health check:
http://localhost:8000/health

3️⃣ Frontend (Next.js)
cd ../web
pnpm install
pnpm dev


Frontend will run at:
http://localhost:3000

It should automatically call your FastAPI /health route if configured.

4️⃣ Chrome Extension (MV3)

Open Chrome.

Go to: chrome://extensions

Enable Developer Mode (top right).

Click Load unpacked.

Select the /extension folder inside the repo.

To verify it’s working:

Open any webpage

Open DevTools → Console

You should see: "Blinders extension active"

🌍 Deployment
Backend

Deploy on:

Railway, Render, or Fly.io

Make sure to set:
DATABASE_URL · JWT_SECRET

Frontend

Deploy on Vercel.

Required environment variable:

NEXT_PUBLIC_API_URL=https://your-backend-url.com

Database

Recommended: Supabase or Neon (both free-tier friendly)
