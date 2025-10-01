from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import FAQ
from schemas import ChatQuery, ChatResponse
from services.matcher import FAQMatcher

router = APIRouter(prefix="/api/chat", tags=["chat"])
matcher = FAQMatcher()   # cache en memoria

def rebuild_index(db: Session):
    items = [(f.id, f.question) for f in db.query(FAQ).all()]
    matcher.build(items)

@router.post("/query", response_model=ChatResponse)
def query_chat(body: ChatQuery, db: Session = Depends(get_db)):
    # reconstruye perezosamente si no hay índice
    if matcher.matrix is None:
        rebuild_index(db)

    results = matcher.query(body.message, top_k=3)
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
        return ChatResponse(answer="No comprendí bien tu consulta. ¿Te refieres a alguna de estas?", intent="fallback", confidence=final, suggestions=sugs)
