from __future__ import annotations
from sqlalchemy import text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.db.db import engine
from server.routers.images import router as images_router
from server.routers.votes import router as votes_router

app = FastAPI(title="gallery-votes", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["meta"])
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"ok": True}

# mount routers
app.include_router(images_router)
app.include_router(votes_router)