from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    preferences: Optional[Dict[str, Any]] = None
    created_at: str

class UploadResponse(BaseModel):
    id: str
    filename: str
    type: str
    status: str
    
class ExtractedKnowledge(BaseModel):
    type: str
    topic: str
    value: str
    pattern: str
    
class InsightResponse(BaseModel):
    id: str
    insight_text: str
    comparison: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    confidence_score: float
    validation_passed: bool
    created_at: str
