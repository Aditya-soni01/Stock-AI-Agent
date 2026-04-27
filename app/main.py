from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from threading import Thread
from pathlib import Path

from app.api.analyze import router
from app.api.routes import stock, market
from app.core.scheduler import start_scheduler
from app.api.routes import upstox_live
try:
    from app.api.routes import forex
except Exception:
    forex = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("Starting background services...")
    start_scheduler()
    try:
        from app.agents.forex_market_agent import start_market_feed
        Thread(target=start_market_feed, daemon=True).start()
    except Exception as exc:
        print(f"Forex market feed disabled: {exc}")
    yield
    # SHUTDOWN
    print("Shutting down services...")


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


@app.get("/debug/routes", include_in_schema=False)
def debug_routes():
    route_rows = []
    for route in app.router.routes:
        path = getattr(route, "path", None)
        if not path:
            continue
        methods = sorted(list(getattr(route, "methods", set()) or set()))
        route_rows.append(
            {
                "path": path,
                "name": getattr(route, "name", None),
                "methods": methods,
            }
        )

    route_rows.sort(key=lambda r: (r["path"], ",".join(r["methods"])))
    return {
        "module": __name__,
        "module_file": __file__,
        "cwd": str(Path.cwd()),
        "routes_count": len(route_rows),
        "routes": route_rows,
    }


# Routers
app.include_router(router)
app.include_router(stock.router, prefix="/api/stock", tags=["Stock"])
app.include_router(market.router, prefix="/market/india", tags=["Indian Market"])
# app.include_router(upstox.router, prefix="/upstox", tags=["Upstox"])
# app.include_router(upstox_router.router, prefix="/upstoxr", tags=["Upstox Auth"])
app.include_router(upstox_live.router, prefix="/upstox", tags=["Upstox Live"])
if forex is not None:
    app.include_router(forex.router, prefix="/forex", tags=["Forex"])
    app.include_router(forex.router, prefix="/forex", tags=["Forex Trading"])
