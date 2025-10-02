import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models import FAQ
from schemas import ChatQuery, ChatResponse
from services.matcher import FAQMatcher, normalize

router = APIRouter(prefix="/api/chat", tags=["chat"])
matcher = FAQMatcher()

def rebuild_index(db: Session):
    items = [(f.id, f.question) for f in db.query(FAQ).all()]
    matcher.build(items)

# ====== Small talk ======
GREETING_MSG = "¡Hola! Pregúntame sobre contraseñas, facturas, precios o ventas."
BYE_MSG = "¡Que tengas un buen día! Si tienes más consultas, no dudes en preguntar. 🙂"

# Trabajamos sobre texto normalizado (minúsculas, sin tildes, sin signos)
GREETING_RE = re.compile(r"^(hola|buenas|buenos dias|buen dia|buenas tardes|buenas noches)\b")
THANKS_RE   = re.compile(r"\b(gracias|muchas gracias|ok|okay|okey|listo|perfecto)\b")

@router.post("/query", response_model=ChatResponse)
def query_chat(body: ChatQuery, db: Session = Depends(get_db)):
    # reconstruye perezosamente si no hay índice
    if matcher.matrix is None:
        rebuild_index(db)

    # --- Small talk primero ---
    text_norm = normalize(body.message)
    if GREETING_RE.search(text_norm):
        return ChatResponse(answer=GREETING_MSG, intent="greeting", confidence=1.0, suggestions=[])
    if THANKS_RE.search(text_norm):
        return ChatResponse(answer=BYE_MSG, intent="closing", confidence=1.0, suggestions=[])

    # --- Buscador de FAQs ---
    results = matcher.query(body.message, top_k=12)

    # Umbrales explicables
    HIGH, MID = 0.80, 0.55
    if not results:
        return ChatResponse(answer="No tengo respuestas aún.", intent="empty", confidence=0.0, suggestions=[])

    # buscar datos de las FAQs top
    ids = [r[0] for r in results]
    faqs = {f.id: f for f in db.query(FAQ).filter(FAQ.id.in_(ids)).all()}

    fid, final, _, _ = results[0]
    top = faqs.get(fid)

    if final >= HIGH:
        return ChatResponse(answer=top.answer, intent="faq", confidence=final, suggestions=[])
    elif final >= MID:
        # sugerencias: títulos de las preguntas
        sugs = [faqs[r[0]].question for r in results]
        return ChatResponse(answer=top.answer, intent="faq_suggest", confidence=final, suggestions=sugs)
    else:
        sugs = [faqs[r[0]].question for r in results]
        return ChatResponse(
            answer="No comprendí bien tu consulta. ¿Te refieres a alguna de estas?",
            intent="fallback",
            confidence=final,
            suggestions=sugs
        )
