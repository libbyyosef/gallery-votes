Gallery Votes — React + FastAPI

A tiny image gallery where users can like or dislike photos, view in fullscreen, navigate with keyboard/arrows, and export votes to CSV.
Backend is FastAPI + PostgreSQL; frontend is React (TypeScript) + Chakra UI with lightweight client state.

Features

🖼️ Grid of 100 Picsum images (stable by id).

👍👎 One reaction per user per image (like, dislike, or none).

⚡ Optimistic UI updates; counts stored in DB.

⤢ Fullscreen modal with left/right navigation and Esc to close.

⌨️ Keyboard: ← / → prev/next, Esc close.

⬇️ Export CSV of the current gallery state (client-side).

📱 Responsive layout (cards flow to fill available width).

Tech Stack

Frontend: React 18, TypeScript, Vite, Chakra UI, react-icons, Jotai

Backend: FastAPI, SQLAlchemy (2.x), Psycopg (v3), PostgreSQL

Images: https://picsum.photos
 (/id/{id}/600/400.webp)

Project Structure
.
├─ client/                     # React app
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ ImageCard.tsx
│  │  │  └─ FullscreenModal.tsx
│  │  ├─ state/images.ts       # jotai atoms
│  │  ├─ api.ts                # fetch/applyReaction helpers
│  │  ├─ reaction.ts           # REACTION constants & types
│  │  ├─ export.ts             # client CSV export
│  │  └─ App.tsx
│  └─ .env.local               # VITE_API_BASE_URL
└─ server/
   ├─ main.py                  # FastAPI app
   ├─ db/db.py                 # engine + SessionLocal
   ├─ models/                  # ImageModel, Base
   ├─ schemas/                 # ImageSchema, ActionResultSchema
   ├─ crud/                    # image_crud (get_all_images, counters, like/unlike, etc.)
   ├─ routers/                 # images router
   ├─ sql_db/schema.sql        # tables & indexes
   └─ scripts/
      ├─ setup_db.py           # apply schema + seed
      └─ seed_images.py        # grabs 100 picsum ids

API (backend)

Base URL: http://localhost:8000

Method	Path	Description
GET	/images/get_all_images	List all images with counters
GET	/images/counters?ids=1&ids=2	Get {image_id, likes, dislikes} for ids
POST	/images/like/{image_id}	Increment like
POST	/images/unlike/{image_id}	Decrement like (not below 0)
POST	/images/dislike/{image_id}	Increment dislike
POST	/images/undislike/{image_id}	Decrement dislike (not below 0)

CSV export is done client-side so we can include the current user’s reaction.

CSV Export (client)

Click Export CSV in the header.
Columns:

image_url — Picsum URL for the image

likes — current like count (from DB)

dislikes — current dislike count (from DB)

current_user_like — true|false (derived from local reaction)

current_user_dislike — true|false (derived from local reaction)

Getting Started
0) Prerequisites

Python 3.10+

Node 18+ (or 20+)

PostgreSQL 14+ running locally

1) Backend
cd server
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
# or install your deps: fastapi uvicorn sqlalchemy psycopg[binary] pydantic ...


Set your DB connection (defaults shown in server/db/db.py):

export DATABASE_URL="postgresql+psycopg://app:app@localhost:5432/app"


Create schema and seed 100 images:

python -m server.scripts.setup_db


Run the API:

uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

2) Frontend
cd client
npm install


Create client/.env.local:

VITE_API_BASE_URL=http://localhost:8000


Start dev server:

npm run dev
# open the URL it prints (usually http://localhost:5173)

Usage Tips

Click an image to open Fullscreen; use ← / → to move, Esc to close.

Hover an image: like/dislike buttons are in the bottom overlay (also shown in fullscreen).

Reactions are “Instagram-style”: like ↔ none ↔ dislike (only one at a time).

The grid auto-fills the row with as many cards as fit your viewport.

Troubleshooting

404 on /images/like/{id}
Ensure you’re hitting the FastAPI server base (VITE_API_BASE_URL) and the images router is included in server/main.py.

CORS
If you serve the frontend from a different origin, make sure FastAPI has CORS middleware configured to allow it.

Picsum blocked / slow
Check your network; the app builds URLs like https://picsum.photos/id/{id}/600/400.webp.

Chakra icon package missing
@chakra-ui/icons isn’t required for this project (we use react-icons). If you add Chakra icons, run:
npm i @chakra-ui/icons @chakra-ui/react @emotion/react @emotion/styled framer-motion

