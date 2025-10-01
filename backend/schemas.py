from pydantic import BaseModel, ConfigDict
from typing import Optional

class FAQCreate(BaseModel):
    question: str
    answer: str
    tags: Optional[str] = None

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    tags: Optional[str] = None

class FAQOut(BaseModel):
    id: int
    question: str
    answer: str
    tags: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class ChatQuery(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    suggestions: list[str] = []
