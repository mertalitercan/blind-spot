"""BlindSpot — Multi-agent fraud detection system. Built with Railtracks."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import demo, transactions, dashboard, websocket_router
from database import init_db, seed_historical_sessions

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="BlindSpot",
    description="AI-powered fraud detection using multi-agent behavioral analysis. Built with Railtracks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demo.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)
app.include_router(websocket_router.router)


@app.on_event("startup")
async def startup():
    init_db()
    seed_historical_sessions()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "blindspot", "framework": "railtracks"}
