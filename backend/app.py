from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine
from models import FAQ
from routes import chat, faq

app = FastAPI(title="ChatBot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"ok": True, "service": "ChatBot API", "docs": "/docs"}

app.include_router(chat.router)
app.include_router(faq.router)
