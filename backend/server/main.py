from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routers.images import router as images_router

app = FastAPI(title="Gallery Votes (counters-only)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# NO '/api' prefix
app.include_router(images_router)
