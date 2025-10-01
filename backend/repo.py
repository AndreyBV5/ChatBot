from sqlalchemy.orm import Session
from models import FAQ
from schemas import FAQCreate, FAQUpdate

def list_faq(db: Session, search: str | None = None, limit=50, offset=0):
    q = db.query(FAQ)
    if search:
        like = f"%{search}%"
        q = q.filter((FAQ.question.like(like)) | (FAQ.answer.like(like)) | (FAQ.tags.like(like)))
    return q.order_by(FAQ.id.desc()).offset(offset).limit(limit).all()

def get_faq(db: Session, faq_id: int):
    return db.query(FAQ).get(faq_id)

def create_faq(db: Session, data: FAQCreate):
    faq = FAQ(question=data.question, answer=data.answer, tags=data.tags)
    db.add(faq); db.commit(); db.refresh(faq)
    return faq

def update_faq(db: Session, faq_id: int, data: FAQUpdate):
    faq = get_faq(db, faq_id)
    if not faq: return None
    if data.question is not None: faq.question = data.question
    if data.answer   is not None: faq.answer   = data.answer
    if data.tags     is not None: faq.tags     = data.tags
    db.commit(); db.refresh(faq)
    return faq

def delete_faq(db: Session, faq_id: int):
    faq = get_faq(db, faq_id)
    if not faq: return False
    db.delete(faq); db.commit()
    return True
