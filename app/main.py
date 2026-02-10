from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from threading import Thread

from app.api.analyze import router
from app.api.routes import stock, market, upstox, upstox_router
from app.agents.upstox_market_agent import start_market_feed
from app.core.scheduler import start_scheduler
from app.api.routes import upstox_live
from app.api.routes import forex



@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("🚀 Starting background services...")
    start_scheduler()
    Thread(target=start_market_feed, daemon=True).start()
    yield
    # SHUTDOWN
    print("🛑 Shutting down services...")


app = FastAPI(
    title="Stock AI Agent",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "running"}


# Routers
app.include_router(router)
app.include_router(stock.router, prefix="/api/stock", tags=["Stock"])
# app.include_router(market.router, prefix="/market/india", tags=["Indian Market"])
# app.include_router(upstox.router, prefix="/upstox", tags=["Upstox"])
# app.include_router(upstox_router.router, prefix="/upstoxr", tags=["Upstox Auth"])
# app.include_router(upstox_live.router, prefix="/upstox", tags=["Upstox Live"])
app.include_router(forex.router, prefix="/forex", tags=["Forex"])
app.include_router(forex.router, prefix="/forex", tags=["Forex Trading"])