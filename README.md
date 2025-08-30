# Gallery Votes

Browse a gallery of images and vote 👍/👎.  
Open any image fullscreen, navigate with arrow keys, and export your votes to CSV.

---

## Run with Docker

> Make sure **Docker** and classic **docker-compose** are installed.

```bash
git clone https://github.com/libbyyosef/gallery-votes.git
cd gallery-votes
docker-compose up --build
```

- **Web UI** → http://localhost:8080
- **API** → http://localhost:8000

### Stop & clean

```bash
# Stop: Ctrl+C in the compose terminal
docker-compose down -v
```

## Project structure

```
.
├─ client/                          # React app (Vite + Chakra UI)
│  ├─ src/
│  │  ├─ components/                # ImageCard, FullscreenModal, etc.
│  │  ├─ reaction.ts                # Reaction enum (LIKE/DISLIKE)
│  │  └─ App.tsx
│  ├─ src/test/                     # Vitest + Testing Library setup & tests
│  ├─ docker/nginx.conf             # Nginx hosts SPA + proxies /images → backend
│  └─ Dockerfile                    # Multi-stage: build (Node) → serve (Nginx)
│
├─ server/                          # FastAPI backend
│  ├─ crud/                         # DB access helpers
│  ├─ db/                           # Session/engine utilities
│  ├─ docker/                       # Container entrypoint scripts
│  ├─ models/                       # SQLAlchemy models
│  ├─ routers/                      # API routes (e.g. /images)
│  ├─ schemas/                      # Pydantic I/O models
│  ├─ scripts/                      # bootstrap helpers (wait, migrate, seed)
│  ├─ sql_db/                       # DB bootstrap SQL (schema + seed)
│  ├─ tests/                        # Pytest tests
│  ├─ main.py                       # FastAPI app entry
│  ├─ requirements.txt              # Prod deps
│  ├─ requirements-test.txt         # Test-only deps
│  └─ Dockerfile                    # Python 3.11 slim image
│
├─ docker-compose.yml               # postgres + backend + web
├─ .env                             # backend env (used by compose)
├─ .env.dev                         # local dev env (ignored in Docker)
├─ .env.docker                      # docker-only env (loaded by compose)
└─ README.md
```

The database runs inside Docker and is initialized automatically (schema + seed).
The web container (Nginx) serves the SPA and proxies `/images/*` to the backend.

## Tech stack

### Frontend
- React + Vite + TypeScript
- Chakra UI
- Jotai (state)
- Vitest + Testing Library (jsdom)

### Backend
- FastAPI
- SQLAlchemy 2.x + Psycopg
- Pydantic

### Infra
- PostgreSQL
- Nginx (SPA hosting + reverse proxy)
- Docker & docker-compose