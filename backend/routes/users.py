from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import structlog
import json
from database.fluxbase import db_client
from database.schemas import UserResponse, UserCreate

logger = structlog.get_logger()
router = APIRouter(prefix="/api/users", tags=["Users"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Extremely basic registration for prototype
    user_id = str(uuid.uuid4())
    
    # Check if exists
    rows = await db_client.execute(f"SELECT id FROM users WHERE email = '{user.email}'")
    if rows:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    await db_client.insert("users", {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "password_hash": user.password, # Plaintext for demo, should hash in prod
        "preferences": "{}"
    })
    
    return UserResponse(
        id=user_id,
        name=user.name,
        email=user.email,
        preferences={},
        created_at="now"
    )

@router.post("/login", response_model=UserResponse)
async def login_user(req: LoginRequest):
    sql = f"SELECT * FROM users WHERE email = '{req.email}' AND password_hash = '{req.password}'"
    rows = await db_client.execute(sql)
    
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    user = rows[0]
    prefs = {}
    if user.get("preferences"):
        try:
            prefs = json.loads(user["preferences"])
        except:
            pass
            
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        preferences=prefs,
        created_at=user.get("created_at", "")
    )
