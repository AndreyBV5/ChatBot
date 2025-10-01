from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db import get_db
from repo import list_faq, get_faq, create_faq, update_faq, delete_faq
from schemas import FAQCreate, FAQOut, FAQUpdate
from routes.chat import rebuild_index   

router = APIRouter(prefix="/api/faq", tags=["faq"])

@router.get("", response_model=list[FAQOut])
def _list(
    search: str | None = Query(None),
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size
    return list_faq(db, search=search, limit=page_size, offset=offset)

@router.post("", response_model=FAQOut, status_code=201)
def _create(body: FAQCreate, db: Session = Depends(get_db)):
    created = create_faq(db, body)
    rebuild_index(db)                    
    return created

@router.put("/{faq_id}", response_model=FAQOut)
def _update(faq_id: int, body: FAQUpdate, db: Session = Depends(get_db)):
    faq = update_faq(db, faq_id, body)
    if not faq:
        raise HTTPException(404, "FAQ not found")
    rebuild_index(db)                    
    return faq

@router.delete("/{faq_id}")
def _delete(faq_id: int, db: Session = Depends(get_db)):
    ok = delete_faq(db, faq_id)
    if not ok:
        raise HTTPException(404, "FAQ not found")
    rebuild_index(db)                   
    return {"ok": True}
