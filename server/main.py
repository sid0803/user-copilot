import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

# Add project root to path to import from heartbeat_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from heartbeat_app.db.models import DatabaseManager
from heartbeat_app.core.config_manager import Config
from heartbeat_app.connectors.slack import SlackConnector
from heartbeat_app.connectors.health import HealthCheckConnector
from heartbeat_app.connectors.git_conn import GitConnector
from heartbeat_app.connectors.file_project import FileProjectConnector
from heartbeat_app.connectors.gmail_conn import GmailConnector
from heartbeat_app.connectors.github_conn import GitHubConnector
from heartbeat_app.connectors.notion_conn import NotionConnector
from heartbeat_app.core.processor import EventProcessor
from classifier import Classifier
from summarizer import Summarizer
from heartbeat_app.delivery.unified_notifier import UnifiedNotifier
from server.auth import verify_password, get_password_hash, create_access_token, decode_access_token

app = FastAPI(title="Heartbeat Intelligence API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Schemas ---
class UserRegister(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DigestOut(BaseModel):
    timestamp: str
    content: str
    source_type: str

# --- Auth Helpers ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_01_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    # Fetch user from DB
    conn = db._get_conn() # Assuming we add _get_conn or just query
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user[0], "email": user[1]}

# --- Routes ---

@app.post("/register", response_model=Token)
def register(user: UserRegister):
    hashed = get_password_hash(user.password)
    conn = db._get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (user.email, hashed))
        conn.commit()
    except:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = cursor.lastrowid
    db.seed_mock_connectors(user_id) # ⚡ Seed mocks for MVP
    conn.close()
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = db._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (form_data.username,))
    row = cursor.fetchone()
    conn.close()
    if not row or not verify_password(form_data.password, row[0]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/digests", response_model=List[DigestOut])
def get_digests(current_user: dict = Depends(get_current_user)):
    conn = db._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, content, source_type FROM digests WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50", (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": r[0], "content": r[1], "source_type": r[2]} for r in rows]

@app.post("/heartbeat/trigger")
def trigger_heartbeat(current_user: dict = Depends(get_current_user)):
    # 1. Load user config from DB
    conn = db._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT connector_type, config_json FROM connector_configs WHERE user_id = ? AND is_active = 1", (current_user["id"],))
    configs = cursor.fetchall()
    conn.close()

    # Convert configs to dict for Config class
    user_settings = {"connectors": {}}
    for c_type, c_json in configs:
        user_settings["connectors"][c_type] = json.loads(c_json)
    
    # We also need AI keys and delivery settings. For MVP, we might use system defaults or user-provided keys.
    # For now, let's assume we use shared environment variables if not in user_settings.
    config = Config(config_dict=user_settings)

    # 2. Re-use Heartbeat Logic (Simplified version of heartbeat.py)
    # Note: We should refactor run_heartbeat to be a reusable function in a service layer.
    try:
        from server.api_logic import run_heartbeat_for_user
        digest = run_heartbeat_for_user(current_user["id"], config)
        return {"status": "success", "digest": digest}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a helper to get DB connection
def _get_conn():
    import sqlite3
    return sqlite3.connect(db.db_path)

db._get_conn = _get_conn
