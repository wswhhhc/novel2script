from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_database
from app.routers import chapters, projects, script

app = FastAPI(title="Novel2Script Backend")
init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chapters.router)
app.include_router(script.router)
app.include_router(projects.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "novel2script-backend"}
