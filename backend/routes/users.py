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
        except Exception:
            pass
            
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        preferences=prefs,
        created_at=str(user.get("created_at", ""))
    )

class UpdatePreferencesRequest(BaseModel):
    preferences: dict

@router.get("/{user_id}/profile", response_model=UserResponse)
async def get_user_profile(user_id: str):
    """Fetch user profile including current saved preferences."""
    safe_user_id = user_id.replace("'", "''")
    rows = await db_client.execute(f"SELECT id, name, email, preferences, created_at FROM users WHERE id = '{safe_user_id}'")
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")
        
    user = rows[0]
    prefs = {}
    if user.get("preferences"):
        try:
            raw_prefs = user["preferences"]
            prefs = json.loads(raw_prefs) if isinstance(raw_prefs, str) else raw_prefs
        except Exception:
            prefs = {}
            
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        preferences=prefs,
        created_at=str(user.get("created_at", ""))
    )

@router.put("/{user_id}/preferences")
async def update_user_preferences(user_id: str, req: UpdatePreferencesRequest):
    """Validate and persist user persona and generation preferences."""
    safe_user_id = user_id.replace("'", "''")
    
    # Check user existence
    check_rows = await db_client.execute(f"SELECT id FROM users WHERE id = '{safe_user_id}'")
    if not check_rows:
        raise HTTPException(status_code=404, detail="User not found")
        
    preferences = req.preferences
    if not isinstance(preferences, dict):
        raise HTTPException(status_code=400, detail="Preferences must be a JSON object")

    # Validate allowed and recognized fields
    valid_keys = {"topics_of_interest", "preferred_tone", "focus_era", "actionability_level"}
    clean_prefs = {}
    for k, v in preferences.items():
        if k in valid_keys:
            if k == "topics_of_interest":
                if isinstance(v, str):
                    clean_prefs[k] = [t.strip() for t in v.split(",") if t.strip()]
                elif isinstance(v, list):
                    clean_prefs[k] = [str(t).strip() for t in v if str(t).strip()]
                else:
                    raise HTTPException(status_code=400, detail="topics_of_interest must be a list of strings or comma-separated string")
            elif isinstance(v, str):
                clean_prefs[k] = v.strip()
            else:
                clean_prefs[k] = v
        else:
            # Allow custom fields as strings/numbers
            clean_prefs[k] = v

    prefs_json = json.dumps(clean_prefs)
    safe_prefs_json = prefs_json.replace("'", "''")
    
    await db_client.execute(f"UPDATE users SET preferences = '{safe_prefs_json}' WHERE id = '{safe_user_id}'")
    logger.info("user_preferences_updated", user_id=user_id, preferences=clean_prefs)
    
    return {
        "success": True,
        "message": "Preferences updated successfully",
        "preferences": clean_prefs
    }
