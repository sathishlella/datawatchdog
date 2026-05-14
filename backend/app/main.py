import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import datasets, rules, reports, schedules
from app.core.scheduler import get_scheduler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = get_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="DataWatchdog API", version="1.0.0", lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(rules.router, prefix="/api/datasets", tags=["rules"])
app.include_router(reports.router, prefix="/api/datasets", tags=["reports"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "datawatchdog"}
