from fastapi import FastAPI
from app.api.analyze import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stock AI Agent")

origins = [
    "http://localhost:5173",   # Vite
    "http://localhost:3000",   # React
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

app.include_router(router)
