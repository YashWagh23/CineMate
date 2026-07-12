import base64
import hashlib
import os
import pickle
import re
import sqlite3
from datetime import date, datetime, timedelta
import random
from io import BytesIO
import smtplib
from email.message import EmailMessage
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
import urllib.parse
import base64 as b64

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ================= CONFIG =================
def load_dotenv_local(path=".env"):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                os.environ.setdefault(key, val)
    except Exception:
        pass

load_dotenv_local()

def render_logo(height=52):
    logo_path = os.path.join("assets", "logo.png")
    col1, col2 = st.columns([1, 5])
    with col1:
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
            st.image(logo_path, width=240)
        else:
            st.write("Cinemate")
    with col2:
        st.write("")
# ================= STYLES =================
def load_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
:root {
    --bg1: #050505;
    --bg2: #0b0b1a;
    --card: rgba(20,20,20,0.75);
    --line: rgba(255,255,255,0.12);
    --accent: #E50914;
    --accent2: #E50914;
    --text: #f5f5f5;
}
.stApp {
    background: radial-gradient(1200px 800px at 20% 0%, #141414 0%, var(--bg1) 40%, var(--bg2) 100%);
    color: var(--text);
    animation: fadein 0.4s ease-in;
    font-family: "Inter", "Segoe UI", sans-serif;
}
[data-testid="stAppViewContainer"].auth-bg {
    background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                url("assets/background.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 100vh;
}
@keyframes fadein {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0.5rem 0 0.75rem 0;
}
.card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(0,0,0,0.35);
}
.hero {
    background: linear-gradient(130deg, rgba(229,9,20,0.18), rgba(229,9,20,0.08));
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 18px;
}
.stButton>button {
    background-color: #e50914 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    border: none !important;
    font-weight: bold !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    background-color: #ff1f1f !important;
    transform: scale(1.05) !important;
    box-shadow: 0 0 10px #e50914 !important;
}
.link-btn {
    display: inline-block;
    text-decoration: none;
    padding: 0.35rem 0.7rem;
    border-radius: 10px;
    background: var(--accent);
    color: #ffffff;
    font-weight: 700;
    font-size: 0.9rem;
    transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}
.link-btn:hover {
    background: #ff1f2f;
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 8px 18px rgba(229,9,20,0.35);
}
section[data-testid="stSidebar"] {
    background: #0b0b0b;
    color: var(--text);
}
.stImage img {
    border-radius: 14px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stImage img:hover {
    transform: scale(1.03);
    box-shadow: 0 16px 34px rgba(0,0,0,0.45);
}
.section-title {
    letter-spacing: 0.3px;
}
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stTextArea>div>textarea {
    background: #121212;
    color: var(--text);
    border: 1px solid var(--line);
}
.stTextInput>div>div>input:focus,
.stSelectbox>div>div>div:focus,
.stTextArea>div>textarea:focus {
    border: 1px solid var(--accent);
    outline: none;
}
.seat {
    display: inline-block;
    padding: 6px 8px;
    border-radius: 8px;
    font-weight: 700;
    text-align: center;
    width: 44px;
    border: 1px solid var(--line);
    margin-bottom: 6px;
    cursor: pointer;
}
.seat-available {
    background: rgba(229, 9, 20, 0.12);
    color: #ffffff;
}
.seat-selected {
    background: rgba(229, 9, 20, 0.35);
    color: #ffffff;
}
.seat-booked {
    background: rgba(229, 9, 20, 0.2);
    color: #ffffff;
}
.legend-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
}
.seat-grid [data-testid="stCheckbox"] label {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid var(--line);
    font-weight: 700;
    background: rgba(229, 9, 20, 0.12);
    color: #ffffff;
    cursor: pointer;
    margin-bottom: 6px;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}
.seat-grid [data-testid="stCheckbox"] label:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
.seat-grid [data-testid="stCheckbox"] input[type="checkbox"] {
    display: none;
}
.seat-grid [data-testid="stCheckbox"] label:has(input:checked) {
    background: rgba(229, 9, 20, 0.35);
    color: #ffffff;
}
.seat-grid [data-testid="stCheckbox"] label:has(input:disabled) {
    background: rgba(229, 9, 20, 0.2);
    color: #ffffff;
    cursor: not-allowed;
}
.seat-row-label {
    font-weight: 700;
    color: #cbd5f5;
    padding-top: 6px;
}
.seat-tier-legend {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid var(--line);
    margin-right: 8px;
    font-size: 0.85rem;
}
.tier-gold { background: rgba(229, 9, 20, 0.2); color: #ffffff; }
.tier-silver { background: rgba(229, 9, 20, 0.18); color: #ffffff; }
.tier-regular { background: rgba(229, 9, 20, 0.15); color: #ffffff; }
.booking-steps {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}
.booking-step {
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--line);
    background: rgba(255,255,255,0.04);
    font-size: 0.85rem;
}
.booking-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}
.summary-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    position: sticky;
    top: 16px;
}
.pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    border: 1px solid var(--line);
    margin: 4px 6px 4px 0;
    background: rgba(255,255,255,0.04);
}
.pill-active {
    background: rgba(252, 191, 73, 0.22);
    color: #fff7ed;
}
.theatre-card {
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 12px;
    background: rgba(255,255,255,0.04);
}
.theatre-card.pill-active {
    background: rgba(229, 9, 20, 0.2);
    color: #ffffff;
    border-color: rgba(229, 9, 20, 0.6);
}
.theatre-card:hover {
    box-shadow: 0 10px 24px rgba(0,0,0,0.25);
}
.ticket-card {
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    background: rgba(255,255,255,0.05);
}
.profile-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
}
.avatar-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: rgba(229,9,20,0.2);
    border: 1px solid rgba(229,9,20,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 8px;
}
.profile-label {
    color: #cbd5f5;
    font-size: 0.85rem;
}
.payment-card {
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
    background: rgba(255,255,255,0.05);
}
.chat-wrap {
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 12px;
    background: rgba(255,255,255,0.03);
    max-height: 520px;
    overflow-y: auto;
}
.bubble {
    padding: 10px 12px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 80%;
}
.bubble.user {
    background: rgba(229, 9, 20, 0.25);
    margin-left: auto;
}
.bubble.ai {
    background: rgba(255,255,255,0.08);
    border-left: 3px solid #ef4444;
}
.msg-row {
    display: flex;
}
.msg-row.user {
    justify-content: flex-end;
}
.msg-row.ai {
    justify-content: flex-start;
}
.stTabs [data-baseweb="tab-list"] {
    justify-content: flex-start !important;
    gap: 15px;
    padding-left: 10px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #bbb !important;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    color: #E50914 !important;
    font-size: 26px !important;
    font-weight: 900 !important;
    border-bottom: 3px solid #E50914;
    text-shadow: 0 0 10px rgba(229, 9, 20, 0.7);
}
.stTabs [data-baseweb="tab"]:hover {
    color: #ffffff !important;
    transform: scale(1.1);
    transition: 0.3s;
}
.logo-link img {
    height: 52px;
    transition: transform 0.2s ease, filter 0.2s ease;
}
.logo-link img:hover {
    transform: scale(1.03);
    filter: drop-shadow(0 0 6px rgba(229,9,20,0.5));
}
.auth-center {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
}
.auth-card {
    background: rgba(0,0,0,0.7);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.45);
}
.admin-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
}
.admin-kpi {
    font-size: 1.6rem;
    font-weight: 800;
}
.admin-label {
    color: #cbd5f5;
    font-size: 0.9rem;
}
.admin-nav-title {
    font-weight: 800;
    margin-bottom: 8px;
}
@media (max-width: 768px) {
    .seat-grid [data-testid="stCheckbox"] label {
        width: 34px;
        height: 28px;
        font-size: 0.75rem;
    }
}
.tag {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 0.7rem;
    border: 1px solid var(--line);
    margin-right: 6px;
    background: rgba(255,255,255,0.06);
}
.tag-green { color: #ffffff; background: rgba(229, 9, 20, 0.22); }
.tag-blue { color: #ffffff; background: rgba(229, 9, 20, 0.2); }
.tag-amber { color: #ffffff; background: rgba(229, 9, 20, 0.2); }
.tag-red { color: #ffffff; background: rgba(229, 9, 20, 0.25); }
.skeleton {
    height: 180px;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0.12), rgba(255,255,255,0.05));
    background-size: 200% 100%;
    animation: shimmer 1.2s infinite;
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
.toast {
    padding: 10px 14px;
    border-radius: 10px;
    background: rgba(34,197,94,0.18);
    color: #dcfce7;
    border: 1px solid rgba(34,197,94,0.4);
    margin-bottom: 10px;
}
.tooltip-seat {
    position: relative;
    cursor: pointer;
}
.tooltip-seat:hover::after {
    content: "Select seat";
    position: absolute;
    top: -28px;
    left: 0;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 4px 6px;
    border-radius: 6px;
    font-size: 0.7rem;
}
.booking-history-card {
    background: #111;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.4);
    display: flex;
    justify-content: space-between;
    gap: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.booking-history-card:hover {
    transform: scale(1.01);
    box-shadow: 0 14px 32px rgba(229,9,20,0.25);
}
.bh-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}
.bh-sub {
    color: #cbd5f5;
    font-size: 0.9rem;
    margin-bottom: 4px;
}
.bh-seat {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: rgba(229,9,20,0.2);
    color: #ffffff;
    border: 1px solid rgba(229,9,20,0.5);
    font-size: 0.85rem;
    margin-bottom: 6px;
}
.bh-id {
    color: #9ca3af;
    font-size: 0.75rem;
}
</style>
""",
        unsafe_allow_html=True
    )

load_css()

# ================= DATABASE =================
conn = sqlite3.connect("app.db", check_same_thread=False)
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT DEFAULT 'user'
)"""
)

c.execute(
    """
CREATE TABLE IF NOT EXISTS bookings(
    username TEXT,
    movie TEXT,
    booking_id TEXT,
    city TEXT,
    theatre TEXT,
    show_time TEXT,
    show_date TEXT,
    seats TEXT,
    total_amount REAL
)
"""
)
conn.commit()

# ================= MIGRATION =================
def ensure_bookings_schema():
    c.execute("PRAGMA table_info(bookings)")
    cols = [row[1] for row in c.fetchall()]
    needed = [
        ("booking_id", "TEXT"),
        ("city", "TEXT"),
        ("theatre", "TEXT"),
        ("show_time", "TEXT"),
        ("show_date", "TEXT"),
        ("seats", "TEXT"),
        ("total_amount", "REAL"),
    ]
    for col, col_type in needed:
        if col not in cols:
            c.execute(f"ALTER TABLE bookings ADD COLUMN {col} {col_type}")
            conn.commit()

ensure_bookings_schema()

c.execute(
    """CREATE TABLE IF NOT EXISTS seat_locks(
    movie TEXT,
    city TEXT,
    theatre TEXT,
    show_time TEXT,
    show_date TEXT,
    seat TEXT,
    username TEXT,
    expires_at TEXT
)"""
)
conn.commit()

# ================= AUTH =================
def ensure_users_schema():
    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]
    needed = [
        ("email", "TEXT"),
        ("password_hash", "TEXT"),
        ("salt", "TEXT"),
        ("created_at", "TEXT"),
        ("is_active", "INTEGER DEFAULT 1"),
        ("profile_image", "TEXT"),
    ]
    for col, col_type in needed:
        if col not in cols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            conn.commit()

ensure_users_schema()

def is_valid_email(email):
    if not email:
        return False
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def password_issues(pw):
    issues = []
    if len(pw) < 8:
        issues.append("at least 8 characters")
    if not re.search(r"[A-Z]", pw):
        issues.append("1 uppercase letter")
    if not re.search(r"[a-z]", pw):
        issues.append("1 lowercase letter")
    if not re.search(r"[0-9]", pw):
        issues.append("1 number")
    if not re.search(r"[^A-Za-z0-9]", pw):
        issues.append("1 special character")
    return issues

def hash_password(pw, salt_b64=None):
    if salt_b64 is None:
        salt = os.urandom(16)
        salt_b64 = base64.b64encode(salt).decode("ascii")
    else:
        salt = base64.b64decode(salt_b64.encode("ascii"))
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, 120000)
    return base64.b64encode(dk).decode("ascii"), salt_b64

def profile_dir():
    path = os.path.join(os.getcwd(), "profile_images")
    os.makedirs(path, exist_ok=True)
    return path

def save_profile_image(username, uploaded_file):
    if not uploaded_file:
        return None
    filename = uploaded_file.name or "profile.png"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg"):
        ext = ".png"
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", username or "user")
    path = os.path.join(profile_dir(), f"{safe_name}{ext}")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def get_profile_image(username):
    c.execute("SELECT profile_image FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        return row[0]
    return None

def register_user(username, email, pw):
    if not is_valid_email(email):
        return False, "Enter a valid email address"
    issues = password_issues(pw)
    if issues:
        return False, "Password must have " + ", ".join(issues)

    c.execute("SELECT 1 FROM users WHERE username=?", (username,))
    if c.fetchone():
        return False, "Username already exists"
    c.execute("SELECT 1 FROM users WHERE email=?", (email,))
    if c.fetchone():
        return False, "Email already exists"

    pw_hash, salt = hash_password(pw)
    created_at = datetime.utcnow().isoformat()
    try:
        c.execute(
            "INSERT INTO users (username,email,password_hash,salt,created_at) VALUES (?,?,?,?,?)",
            (username, email, pw_hash, salt, created_at),
        )
        conn.commit()
        return True, "Account created. Please login."
    except Exception:
        return False, "Registration failed. Try a different username."

def get_user_by_identifier(identifier):
    c.execute(
        "SELECT username, email, password, password_hash, salt, role, is_active FROM users WHERE username=? OR email=?",
        (identifier, identifier),
    )
    return c.fetchone()

def login_user(identifier, pw):
    identifier = identifier.strip() if identifier else identifier
    user = get_user_by_identifier(identifier)
    if not user:
        # Allow one-time admin bootstrap if default credentials are used
        if identifier == "admin" and pw == "admin123":
            new_hash, new_salt = hash_password(pw)
            c.execute(
                "UPDATE users SET password_hash=?, salt=?, password=NULL WHERE username='admin'",
                (new_hash, new_salt),
            )
            conn.commit()
            return get_user_by_identifier("admin")
        return None

    username, email, legacy_pw, pw_hash, salt, role, is_active = user
    if is_active is not None and int(is_active) == 0:
        return None
    if pw_hash and salt:
        check_hash, _ = hash_password(pw, salt_b64=salt)
        if check_hash == pw_hash:
            return user
        return None

    if legacy_pw and legacy_pw == pw:
        new_hash, new_salt = hash_password(pw)
        c.execute(
            "UPDATE users SET password_hash=?, salt=?, password=NULL WHERE username=?",
            (new_hash, new_salt, username),
        )
        conn.commit()
        return get_user_by_identifier(username)

    return None

def ensure_admin_user():
    c.execute("SELECT username, password, password_hash, salt FROM users WHERE username='admin'")
    admin_row = c.fetchone()
    if not admin_row:
        pw_hash, salt = hash_password("admin123")
        c.execute(
            "INSERT INTO users (username, email, password_hash, salt, role, created_at) VALUES (?,?,?,?,?,?)",
            ("admin", "admin@example.com", pw_hash, salt, "admin", datetime.utcnow().isoformat()),
        )
        conn.commit()
    else:
        _, legacy_pw, pw_hash, salt = admin_row
        if (not pw_hash or not salt) and legacy_pw:
            new_hash, new_salt = hash_password(legacy_pw)
            c.execute(
                "UPDATE users SET password_hash=?, salt=?, password=NULL WHERE username='admin'",
                (new_hash, new_salt),
            )
            conn.commit()

    # Secondary admin account (fresh credentials)
    c.execute("SELECT 1 FROM users WHERE username='admin2'")
    if not c.fetchone():
        pw_hash, salt = hash_password("Admin@123")
        c.execute(
            "INSERT INTO users (username, email, password_hash, salt, role, created_at) VALUES (?,?,?,?,?,?)",
            ("admin2", "admin2@example.com", pw_hash, salt, "admin", datetime.utcnow().isoformat()),
        )
        conn.commit()

ensure_admin_user()

# ================= LOAD ML =================
@st.cache_data
def load_models():
    movies_dict = pickle.load(open("movies.pkl", "rb"))
    movies_df = pd.DataFrame(movies_dict)
    sim = pickle.load(open("similarity.pkl", "rb"))
    return movies_df, sim

movies, similarity = load_models()
selected_movie = None

API_KEY = os.getenv("TMDB_API_KEY", "84a2f04db296780859d763c8f71ed855")

# ================= API HELPERS =================
@st.cache_data(ttl=3600)
def fetch_poster(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        data = requests.get(url, timeout=10).json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Image"

@st.cache_data(ttl=3600)
def fetch_trailer(movie_title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
        search_data = requests.get(search_url, timeout=10).json()
        if not search_data.get("results"):
            return None
        movie_id = search_data["results"][0]["id"]

        video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
        video_data = requests.get(video_url, timeout=10).json()

        for vid in video_data.get("results", []):
            if vid.get("type") == "Trailer" and vid.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={vid['key']}"
    except Exception:
        pass
    return None

def get_youtube_id(url):
    if not url:
        return None
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

@st.cache_data(ttl=3600)
def fetch_details(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        data = requests.get(url, timeout=10).json()
        if data.get("results"):
            m = data["results"][0]
            return m.get("vote_average"), m.get("overview"), m.get("release_date")
    except Exception:
        pass
    return None, None, None

@st.cache_data(ttl=3600)
def fetch_movie_full_details(title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        search_data = requests.get(search_url, timeout=10).json()
        if not search_data.get("results"):
            return None
        movie_id = search_data["results"][0]["id"]

        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
        reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={API_KEY}"

        details = requests.get(details_url, timeout=10).json()
        credits = requests.get(credits_url, timeout=10).json()
        reviews = requests.get(reviews_url, timeout=10).json()

        return {
            "details": details,
            "credits": credits,
            "reviews": reviews,
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_trending_movies():
    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        return data.get("results", [])[:10]
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_genre_map():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        return {g["id"]: g["name"] for g in data.get("genres", [])}
    except Exception:
        return {}

@st.cache_data(ttl=3600)
def fetch_now_playing():
    url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        return data.get("results", [])[:12]
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_bollywood_movies():
    url = (
        f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}"
        "&with_original_language=hi&region=IN"
    )
    try:
        data = requests.get(url, timeout=10).json()
        return data.get("results", [])[:12]
    except Exception:
        return []

def normalize_language(code_or_name):
    if not code_or_name:
        return "english"
    mapping = {
        "en": "english",
        "hi": "hindi",
        "ta": "tamil",
        "te": "telugu",
        "english": "english",
        "hindi": "hindi",
        "tamil": "tamil",
        "telugu": "telugu",
    }
    return mapping.get(str(code_or_name).lower(), "english")

def get_browsing_movies():
    c.execute("SELECT COUNT(*) FROM movies_db")
    if c.fetchone()[0] > 0:
        return [
            {
                "title": r[0],
                "poster_path": r[1],
                "overview": r[2],
                "release_date": r[3],
                "vote_average": r[4],
                "language": r[5],
                "genre": r[6],
            }
            for r in c.execute(
                "SELECT title, poster_path, overview, release_date, rating, language, genre FROM movies_db"
            ).fetchall()
        ]

    admin_running = fetch_admin_running_movies()
    now_playing = fetch_now_playing()
    bollywood = fetch_bollywood_movies()

    merged = []
    seen = set()

    for m in admin_running:
        title = m.get("title", "")
        key = title.lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(
                {
                    "title": title,
                    "rating": m.get("rating"),
                    "genre": m.get("genre"),
                    "poster_url": m.get("poster_url"),
                    "language": normalize_language(m.get("language")),
                }
            )

    for m in now_playing:
        title = m.get("title", "")
        key = title.lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(
                {
                    "title": title,
                    "vote_average": m.get("vote_average"),
                    "genre_ids": m.get("genre_ids", []),
                    "poster_path": m.get("poster_path"),
                    "language": normalize_language(m.get("original_language")),
                }
            )

    for m in bollywood:
        title = m.get("title", "")
        key = title.lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(
                {
                    "title": title,
                    "vote_average": m.get("vote_average"),
                    "genre_ids": m.get("genre_ids", []),
                    "poster_path": m.get("poster_path"),
                    "language": "hindi",
                }
            )
    return merged

def rebuild_movie_db(api_key, pages=10):
    c.execute("DELETE FROM movies_db")
    conn.commit()

    def fetch_discover(params, pages):
        results = []
        for p in range(1, pages + 1):
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&page={p}&" + params
            try:
                data = requests.get(url, timeout=10).json()
                results.extend(data.get("results", []))
            except Exception:
                pass
        return results

    english = fetch_discover("language=en-US&sort_by=popularity.desc", pages)
    hindi = fetch_discover("with_original_language=hi&region=IN&sort_by=popularity.desc", pages)
    tamil = fetch_discover("with_original_language=ta&region=IN", pages)
    telugu = fetch_discover("with_original_language=te&region=IN", pages)
    malayalam = fetch_discover("with_original_language=ml&region=IN", pages)
    kannada = fetch_discover("with_original_language=kn&region=IN", pages)

    # Optional keyword boost
    hindi_kw = []
    for q in ["bollywood", "hindi movie"]:
        for p in range(1, pages + 1):
            url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={urllib.parse.quote(q)}&page={p}"
            try:
                data = requests.get(url, timeout=10).json()
                hindi_kw.extend(data.get("results", []))
            except Exception:
                pass

    # Filter Bollywood strictly
    hindi = [m for m in hindi if m.get("original_language") == "hi"]
    hindi_kw = [m for m in hindi_kw if m.get("original_language") == "hi"]

    all_movies = english + hindi + hindi_kw + tamil + telugu + malayalam + kannada
    print("Bollywood count:", len(hindi) + len(hindi_kw))
    print("Hollywood count:", len(english))
    seen = set()
    for m in all_movies:
        tmdb_id = m.get("id")
        if not tmdb_id or tmdb_id in seen:
            continue
        seen.add(tmdb_id)
        lang = m.get("original_language")
        if lang == "en":
            tag = "Hollywood"
        elif lang == "hi":
            tag = "Bollywood"
        else:
            tag = "South Indian"
        genre_ids = m.get("genre_ids", [])
        genre_map = fetch_genre_map()
        genres = [genre_map.get(gid, "") for gid in genre_ids if genre_map.get(gid)]
        c.execute(
            "INSERT INTO movies_db (tmdb_id, title, poster_path, overview, release_date, rating, language, language_tag, genre) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                tmdb_id,
                m.get("title"),
                m.get("poster_path"),
                m.get("overview"),
                m.get("release_date"),
                m.get("vote_average"),
                lang,
                tag,
                ", ".join(genres),
            ),
        )
    conn.commit()

def get_coming_soon_movies():
    c.execute("SELECT title, rating, genre, poster_url, release_date FROM admin_movies WHERE status='Coming Soon'")
    rows = c.fetchall()
    movies = []
    for r in rows:
        movies.append(
            {
                "title": r[0],
                "rating": r[1],
                "genre": r[2],
                "poster_url": r[3],
                "release_date": r[4],
            }
        )
    return movies

def movie_tags(movie):
    tags = []
    rating = movie.get("vote_average", movie.get("rating")) or 0
    if rating >= 7.5:
        tags.append(("Top Rated", "tag-green"))
    if movie.get("release_date"):
        try:
            rd = datetime.fromisoformat(movie.get("release_date"))
            if (datetime.utcnow() - rd).days <= 30:
                tags.append(("New", "tag-blue"))
        except Exception:
            pass
    if movie.get("trending"):
        tags.append(("Trending", "tag-amber"))
    if movie.get("recommended"):
        tags.append(("Recommended", "tag-red"))
    return tags

def apply_language_filter(movies_list, lang_filter):
    if lang_filter == "All Movies":
        return movies_list
    if lang_filter == "Hollywood":
        return [m for m in movies_list if normalize_language(m.get("language")) == "english"]
    if lang_filter == "Bollywood":
        return [m for m in movies_list if normalize_language(m.get("language")) == "hindi"]
    if lang_filter == "South Indian":
        return [
            m
            for m in movies_list
            if normalize_language(m.get("language")) in ("tamil", "telugu")
        ]
    return movies_list

# ================= THEATRES =================
default_theatres_by_city = {
    "Pune": {
        "PVR Phoenix Mall": ["10:00 AM", "1:30 PM", "5:00 PM", "8:30 PM"],
        "INOX Amanora Mall": ["11:00 AM", "2:30 PM", "6:30 PM", "9:30 PM"],
        "Cinepolis Seasons Mall": ["9:30 AM", "12:30 PM", "4:30 PM", "8:00 PM"],
    },
    "Mumbai": {
        "PVR Juhu": ["10:15 AM", "1:45 PM", "5:15 PM", "8:45 PM"],
        "INOX R City": ["11:15 AM", "2:45 PM", "6:15 PM", "9:45 PM"],
        "Cinepolis Andheri": ["9:45 AM", "12:45 PM", "4:45 PM", "8:15 PM"],
    },
}


ROWS = ["A", "B", "C", "D", "E"]
SEATS_PER_ROW = 5
TIER_MAP = {
    "A": ("Gold", 350),
    "B": ("Gold", 350),
    "C": ("Silver", 250),
    "D": ("Regular", 180),
    "E": ("Regular", 180),
}

# ================= RECOMMEND =================
def recommend(movie):
    try:
        matches = movies[movies["title"].str.lower() == movie.lower()]
        if matches.empty:
            return [], [], []

        idx = matches.index[0]
        distances = similarity[idx]

        movie_list = sorted(
            list(enumerate(distances)), reverse=True, key=lambda x: x[1]
        )[1:6]

        names, posters, scores = [], [], []

        for i in movie_list:
            title = movies.iloc[i[0]].title
            names.append(title)
            posters.append(fetch_poster(title))
            scores.append(round(i[1] * 100, 2))

        return names, posters, scores
    except Exception:
        return [], [], []

def build_booking_id():
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rand = random.randint(1000, 9999)
    return f"BKG{ts}{rand}"

def cleanup_expired_locks():
    now_iso = datetime.utcnow().isoformat()
    c.execute("DELETE FROM seat_locks WHERE expires_at < ?", (now_iso,))
    conn.commit()

def get_lock_map(movie, city, theatre, show_time, show_date):
    cleanup_expired_locks()
    c.execute(
        "SELECT seat, username FROM seat_locks WHERE movie=? AND city=? AND theatre=? AND show_time=? AND show_date=?",
        (movie, city, theatre, show_time, show_date),
    )
    return {row[0]: row[1] for row in c.fetchall()}

def lock_seats(movie, city, theatre, show_time, show_date, seats, username, minutes=10):
    cleanup_expired_locks()
    expires_at = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
    for seat in seats:
        c.execute(
            "INSERT INTO seat_locks VALUES (?,?,?,?,?,?,?,?)",
            (movie, city, theatre, show_time, show_date, seat, username, expires_at),
        )
    conn.commit()

def release_seats(movie, city, theatre, show_time, show_date, seats, username):
    cleanup_expired_locks()
    for seat in seats:
        c.execute(
            "DELETE FROM seat_locks WHERE movie=? AND city=? AND theatre=? AND show_time=? AND show_date=? AND seat=? AND username=?",
            (movie, city, theatre, show_time, show_date, seat, username),
        )
    conn.commit()

def send_booking_email(to_email, booking):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("SMTP_EMAIL")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "no-reply@example.com")
    use_tls = os.getenv("SMTP_TLS", "true").lower() == "true"

    print("SMTP EMAIL:", smtp_user)
    print("SMTP PASSWORD:", "Loaded" if smtp_pass else "Missing")

    if not smtp_host or not smtp_user or not smtp_pass or not to_email:
        print("SMTP not configured properly")
        return False, "SMTP not configured"

    html_body = f"""
    <html>
      <body style="font-family:Arial,sans-serif;background:#0b1021;color:#ffffff;padding:24px;">
        <div style="max-width:560px;margin:auto;background:#111836;border-radius:16px;padding:20px;">
          <h2 style="margin-top:0;">Booking Confirmation 🎟️</h2>
          <p><strong>Movie:</strong> {booking['movie']}</p>
          <p><strong>Theatre:</strong> {booking['theatre']}</p>
          <p><strong>Location:</strong> {booking['city']}</p>
          <p><strong>Date & Time:</strong> {booking['show_date']} {booking['show_time']}</p>
          <p><strong>Seats:</strong> {", ".join(booking['seats'])}</p>
          <p><strong>Total Paid:</strong> ₹{booking['price']}</p>
          <p><strong>Booking ID:</strong> {booking['booking_id']}</p>
          <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);" />
          <p style="font-size:12px;color:#cbd5f5;">Thank you for booking with us.</p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your Ticket - {booking['booking_id']}"
    msg["From"] = smtp_from
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText("Your booking confirmation is attached in HTML.", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, "Email sent"
    except Exception as e:
        print(f"Email failed to send: {e}")
        return False, str(e)

def ensure_ratings_schema():
    c.execute(
        """CREATE TABLE IF NOT EXISTS ratings(
        username TEXT,
        movie TEXT,
        rating INTEGER,
        created_at TEXT
    )"""
    )
    conn.commit()

ensure_ratings_schema()

def ensure_admin_schema():
    c.execute(
        """CREATE TABLE IF NOT EXISTS admin_movies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        rating REAL,
        genre TEXT,
        poster_url TEXT,
        language TEXT DEFAULT 'english',
        release_date TEXT,
        status TEXT DEFAULT 'Now Playing',
        is_running INTEGER DEFAULT 1
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS theatres(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        theatre TEXT,
        show_time TEXT,
        movie_title TEXT
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS movies_db(
        tmdb_id INTEGER PRIMARY KEY,
        title TEXT,
        poster_path TEXT,
        overview TEXT,
        release_date TEXT,
        rating REAL,
        language TEXT,
        language_tag TEXT,
        genre TEXT
    )"""
    )
    c.execute("PRAGMA table_info(admin_movies)")
    cols = [row[1] for row in c.fetchall()]
    if "language" not in cols:
        c.execute("ALTER TABLE admin_movies ADD COLUMN language TEXT DEFAULT 'english'")
    if "release_date" not in cols:
        c.execute("ALTER TABLE admin_movies ADD COLUMN release_date TEXT")
    if "status" not in cols:
        c.execute("ALTER TABLE admin_movies ADD COLUMN status TEXT DEFAULT 'Now Playing'")
    c.execute("PRAGMA table_info(theatres)")
    tcols = [row[1] for row in c.fetchall()]
    if "movie_title" not in tcols:
        c.execute("ALTER TABLE theatres ADD COLUMN movie_title TEXT")
    conn.commit()

ensure_admin_schema()

def fetch_admin_running_movies():
    c.execute(
        "SELECT title, rating, genre, poster_url, language FROM admin_movies WHERE is_running=1"
    )
    rows = c.fetchall()
    return [
        {
            "title": r[0],
            "rating": r[1],
            "genre": r[2],
            "poster_url": r[3],
            "language": r[4],
        }
        for r in rows
    ]

def fetch_theatres_from_db():
    c.execute("SELECT city, theatre, show_time FROM theatres")
    rows = c.fetchall()
    theatres = {}
    for city, theatre, show_time in rows:
        theatres.setdefault(city, {})
        theatres[city].setdefault(theatre, [])
        if show_time not in theatres[city][theatre]:
            theatres[city][theatre].append(show_time)
    return theatres

def theatre_availability(movie, city, theatre, show_time, show_date):
    c.execute(
        "SELECT seats FROM bookings WHERE movie=? AND city=? AND theatre=? AND show_time=? AND show_date=?",
        (movie, city, theatre, show_time, str(show_date)),
    )
    booked = set()
    for row in c.fetchall():
        if row[0]:
            booked.update([s.strip() for s in row[0].split(",") if s.strip()])
    total = len(ROWS) * SEATS_PER_ROW
    available = max(total - len(booked), 0)
    if available <= 8:
        tag = "Almost Full"
    elif available <= 18:
        tag = "Fast Filling"
    else:
        tag = "Available"
    return available, tag

theatres_by_city = fetch_theatres_from_db()
if not theatres_by_city:
    theatres_by_city = default_theatres_by_city

def admin_app():
    render_logo()
    st.sidebar.markdown("<div class='admin-nav-title'>Admin Panel</div>", unsafe_allow_html=True)
    nav = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Movies", "Theatres", "Bookings", "Users"],
        label_visibility="collapsed",
    )
    if st.sidebar.button("Logout", key="admin_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = "user"
        st.rerun()

    st.title("Admin Dashboard")

    if nav == "Dashboard":
        c.execute("SELECT COUNT(*) FROM admin_movies")
        total_movies = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM bookings")
        total_bookings = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM theatres")
        total_theatres = c.fetchone()[0]

        cols = st.columns(4)
        with cols[0]:
            st.markdown(
                f"<div class='admin-card'><div class='admin-kpi'>{total_movies}</div><div class='admin-label'>Total Movies</div></div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f"<div class='admin-card'><div class='admin-kpi'>{total_bookings}</div><div class='admin-label'>Total Bookings</div></div>",
                unsafe_allow_html=True,
            )
        with cols[2]:
            st.markdown(
                f"<div class='admin-card'><div class='admin-kpi'>{total_users}</div><div class='admin-label'>Total Users</div></div>",
                unsafe_allow_html=True,
            )
        with cols[3]:
            st.markdown(
                f"<div class='admin-card'><div class='admin-kpi'>{total_theatres}</div><div class='admin-label'>Total Theatres</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("### Admin Insights")
        col_a, col_b = st.columns(2)
        with col_a:
            df_top_movies = pd.read_sql_query(
                "SELECT movie, COUNT(*) as bookings FROM bookings GROUP BY movie ORDER BY bookings DESC LIMIT 5",
                conn,
            )
            if not df_top_movies.empty:
                st.bar_chart(df_top_movies.set_index("movie"))
            else:
                st.info("No bookings yet")
        with col_b:
            df_cities = pd.read_sql_query(
                "SELECT city, COUNT(*) as bookings FROM bookings GROUP BY city ORDER BY bookings DESC LIMIT 5",
                conn,
            )
            if not df_cities.empty:
                st.bar_chart(df_cities.set_index("city"))
            else:
                st.info("No bookings yet")

        df_daily = pd.read_sql_query(
            "SELECT show_date, COUNT(*) as bookings FROM bookings GROUP BY show_date ORDER BY show_date",
            conn,
        )
        if not df_daily.empty:
            st.line_chart(df_daily.set_index("show_date"))

        df_revenue = pd.read_sql_query(
            "SELECT show_date, SUM(total_amount) as revenue FROM bookings GROUP BY show_date ORDER BY show_date",
            conn,
        )
        if not df_revenue.empty:
            st.area_chart(df_revenue.set_index("show_date"))

    if nav == "Movies":
        st.subheader("Movies Management")
        movies_df = pd.read_sql_query("SELECT * FROM admin_movies", conn)
        st.dataframe(movies_df, use_container_width=True)

        if st.button("Rebuild Movie Database from TMDb"):
            rebuild_movie_db(API_KEY, pages=5)
            st.success("Movie database rebuilt.")
 
        st.markdown("### Add Movie")
        with st.form("admin_add_movie_form"):
            title = st.text_input("Title")
            rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            genre = st.text_input("Genre (comma separated)")
            language = st.selectbox("Language", ["english", "hindi"])
            release_date = st.date_input("Release Date")
            status = st.selectbox("Status", ["Now Playing", "Coming Soon"])
            poster_url = st.text_input("Poster URL (optional)")
            poster_file = st.file_uploader("Upload Poster (optional)", type=["png", "jpg", "jpeg"])
            is_running = st.checkbox("Currently Running", value=True)
            submitted = st.form_submit_button("Add Movie")
        if submitted:
            if poster_file:
                os.makedirs("posters", exist_ok=True)
                safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", title.strip().lower())
                file_path = os.path.join("posters", f"{safe_name}.jpg")
                with open(file_path, "wb") as f:
                    f.write(poster_file.read())
                poster_url = file_path
            try:
                c.execute(
                    "INSERT INTO admin_movies (title, rating, genre, poster_url, language, release_date, status, is_running) VALUES (?,?,?,?,?,?,?,?)",
                    (title, rating, genre, poster_url, language, str(release_date), status, 1 if is_running else 0),
                )
                conn.commit()
                st.success("Movie added")
            except Exception:
                st.warning("Movie already exists or invalid data")

        st.markdown("### Edit Movie")
        c.execute("SELECT title FROM admin_movies ORDER BY title")
        titles = [r[0] for r in c.fetchall()]
        if titles:
            selected = st.selectbox("Select Movie", titles, key="edit_movie_select")
            c.execute("SELECT rating, genre, poster_url, language, release_date, status, is_running FROM admin_movies WHERE title=?", (selected,))
            row = c.fetchone()
            if row:
                with st.form("admin_edit_movie_form"):
                    rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=float(row[0] or 7.0), step=0.1)
                    genre = st.text_input("Genre", value=row[1] or "")
                    language = st.selectbox("Language", ["english", "hindi"], index=0 if row[3] == "english" else 1)
                    release_date = st.text_input("Release Date", value=row[4] or "")
                    status = st.selectbox("Status", ["Now Playing", "Coming Soon"], index=0 if row[5] == "Now Playing" else 1)
                    poster_url = st.text_input("Poster URL", value=row[2] or "")
                    is_running = st.checkbox("Currently Running", value=bool(row[6]))
                    saved = st.form_submit_button("Save Changes")
                if saved:
                    c.execute(
                        "UPDATE admin_movies SET rating=?, genre=?, poster_url=?, language=?, release_date=?, status=?, is_running=? WHERE title=?",
                        (rating, genre, poster_url, language, release_date, status, 1 if is_running else 0, selected),
                    )
                    conn.commit()
                    st.success("Movie updated")

            st.markdown("### Delete Movie")
            if st.button("Delete Selected Movie", key="delete_movie_btn"):
                c.execute("DELETE FROM admin_movies WHERE title=?", (selected,))
                conn.commit()
                st.success("Movie deleted")

    if nav == "Theatres":
        st.subheader("Theatres and Shows")
        theatres_df = pd.read_sql_query("SELECT * FROM theatres", conn)
        st.dataframe(theatres_df, use_container_width=True)

        st.markdown("### Add Show")
        with st.form("admin_add_show_form"):
            city = st.text_input("City")
            theatre = st.text_input("Theatre Name")
            show_time = st.text_input("Show Time (e.g., 6:30 PM)")
            c.execute("SELECT title FROM admin_movies ORDER BY title")
            titles = [r[0] for r in c.fetchall()]
            movie_title = st.selectbox("Movie", titles) if titles else st.text_input("Movie Title")
            submitted = st.form_submit_button("Add Showtime")
        if submitted:
            c.execute(
                "INSERT INTO theatres (city, theatre, show_time, movie_title) VALUES (?,?,?,?)",
                (city, theatre, show_time, movie_title),
            )
            conn.commit()
            st.success("Showtime added")

        st.markdown("### Remove Showtime")
        c.execute("SELECT id, city, theatre, show_time FROM theatres ORDER BY city, theatre")
        rows = c.fetchall()
        if rows:
            options = {f"{r[1]} | {r[2]} | {r[3]} (#{r[0]})": r[0] for r in rows}
            choice = st.selectbox("Select Showtime", list(options.keys()))
            theatre_id = options[choice]
            if st.button("Remove Selected Showtime"):
                c.execute("DELETE FROM theatres WHERE id=?", (theatre_id,))
                conn.commit()
                st.success("Showtime removed")

    if nav == "Bookings":
        st.subheader("Bookings Management")
        bookings_df = pd.read_sql_query(
            "SELECT username, movie, theatre, seats, show_time, booking_id FROM bookings",
            conn,
        )
        st.dataframe(bookings_df, use_container_width=True)
        c.execute("SELECT booking_id FROM bookings ORDER BY show_date DESC")
        booking_ids = [r[0] for r in c.fetchall()]
        if booking_ids:
            cancel_id = st.selectbox("Cancel Booking", booking_ids)
            if st.button("Cancel Selected Booking"):
                c.execute("DELETE FROM bookings WHERE booking_id=?", (cancel_id,))
                conn.commit()
                st.success("Booking cancelled")

    if nav == "Users":
        st.subheader("Users Management")
        users_df = pd.read_sql_query("SELECT username, email, role, is_active FROM users", conn)
        st.dataframe(users_df, use_container_width=True)

        c.execute("SELECT username FROM users ORDER BY username")
        user_list = [r[0] for r in c.fetchall()]
        if user_list:
            selected_user = st.selectbox("Select User", user_list)
            if st.button("Disable User"):
                c.execute("UPDATE users SET is_active=0 WHERE username=?", (selected_user,))
                conn.commit()
                st.success("User disabled")
            if st.button("Enable User"):
                c.execute("UPDATE users SET is_active=1 WHERE username=?", (selected_user,))
                conn.commit()
                st.success("User enabled")
            if st.button("Delete User"):
                c.execute("DELETE FROM users WHERE username=?", (selected_user,))
                conn.commit()
                st.success("User deleted")

            st.markdown("### Booking History")
            history = pd.read_sql_query(
                "SELECT movie, theatre, show_date, show_time, seats, booking_id FROM bookings WHERE username=?",
                conn,
                params=(selected_user,),
            )
            st.dataframe(history, use_container_width=True)

def get_user_recent_movies(username, limit=50):
    c.execute(
        "SELECT movie FROM bookings WHERE username=? ORDER BY show_date DESC",
        (username,),
    )
    rows = c.fetchall()
    titles = [r[0] for r in rows if r and r[0]]
    return titles[:limit]

@st.cache_data(ttl=3600)
def fetch_movie_genres(title):
    try:
        search_url = (
            f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        )
        search_data = requests.get(search_url, timeout=10).json()
        if not search_data.get("results"):
            return []
        movie_id = search_data["results"][0]["id"]
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        details = requests.get(details_url, timeout=10).json()
        return [g.get("name") for g in details.get("genres", []) if g.get("name")]
    except Exception:
        return []

def mood_to_genres():
    return {
        "Happy": ["Comedy", "Family", "Animation", "Music"],
        "Sad": ["Drama", "Romance"],
        "Romantic": ["Romance", "Drama"],
        "Excited": ["Action", "Adventure", "Science Fiction", "Fantasy"],
        "Thriller mood": ["Thriller", "Mystery", "Crime", "Horror"],
        "Chill / Relaxed": ["Comedy", "Family", "Animation", "Fantasy"],
    }

def recommend_by_mood(mood, username=None, k=8):
    genres = mood_to_genres().get(mood, [])
    candidates = []
    browsing = get_browsing_movies()
    for m in browsing:
        cand_genres = [g for g in m.get("genre_ids", [])]
        candidates.append(
            {
                "title": m.get("title", ""),
                "poster": (
                    m.get("poster_url")
                    or (
                        "https://image.tmdb.org/t/p/w500" + m["poster_path"]
                        if m.get("poster_path")
                        else None
                    )
                ),
                "rating": m.get("vote_average", m.get("rating")),
                "genre_ids": cand_genres,
            }
        )
    genre_map = fetch_genre_map()
    scored = []
    for cnd in candidates:
        cnd_genres = [genre_map.get(gid, "") for gid in cnd["genre_ids"]]
        genre_match = len(set(genres) & set(cnd_genres))
        score = genre_match * 2
        if cnd.get("rating"):
            score += float(cnd["rating"]) / 10
        scored.append((score, cnd))

    if username:
        recent = get_user_recent_movies(username)
        recent_genres = []
        for title in recent[:5]:
            recent_genres.extend(fetch_movie_genres(title))
        def history_boost(item):
            cnd_genres = [genre_map.get(gid, "") for gid in item["genre_ids"]]
            return len(set(recent_genres) & set(cnd_genres))
        scored = [(s + history_boost(c), c) for s, c in scored]

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]

def get_user_genre_profile(username, limit=5):
    recent = get_user_recent_movies(username, limit=limit)
    recent_genres = []
    for title in recent:
        recent_genres.extend(fetch_movie_genres(title))
    return list(set(recent_genres))

def hybrid_recommendations(username, mood, k=10):
    mood_genres = mood_to_genres().get(mood, [])
    user_genres = get_user_genre_profile(username)
    candidates = get_browsing_movies()
    genre_map = fetch_genre_map()

    scored = []
    for m in candidates:
        title = m.get("title", "")
        if not title:
            continue
        cnd_genres = []
        if m.get("genre_ids"):
            cnd_genres = [genre_map.get(gid, "") for gid in m.get("genre_ids", [])]
        elif m.get("genre"):
            cnd_genres = [g.strip() for g in m.get("genre", "").split(",") if g.strip()]

        mood_match = 0.0
        if mood_genres:
            mood_match = len(set(mood_genres) & set(cnd_genres)) / len(set(mood_genres))

        genre_sim = 0.0
        if user_genres:
            genre_sim = len(set(user_genres) & set(cnd_genres)) / len(set(user_genres))

        popularity = (m.get("vote_average", m.get("rating")) or 0) / 10.0
        user_rating = get_user_rating(username, title)
        user_rating_norm = (user_rating / 5.0) if user_rating else 0.0

        final_score = (
            0.4 * mood_match
            + 0.3 * genre_sim
            + 0.2 * popularity
            + 0.1 * user_rating_norm
        )

        scored.append(
            (
                final_score,
                {
                    "title": title,
                    "poster": m.get("poster_url")
                    or (
                        "https://image.tmdb.org/t/p/w500" + m["poster_path"]
                        if m.get("poster_path")
                        else None
                    ),
                    "rating": m.get("vote_average", m.get("rating")),
                    "genres": cnd_genres,
                },
            )
        )

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]

def upsert_rating(username, movie, rating):
    c.execute(
        "SELECT rating FROM ratings WHERE username=? AND movie=?",
        (username, movie),
    )
    if c.fetchone():
        c.execute(
            "UPDATE ratings SET rating=?, created_at=? WHERE username=? AND movie=?",
            (rating, datetime.utcnow().isoformat(), username, movie),
        )
    else:
        c.execute(
            "INSERT INTO ratings (username, movie, rating, created_at) VALUES (?,?,?,?)",
            (username, movie, rating, datetime.utcnow().isoformat()),
        )
    conn.commit()

def get_user_rating(username, movie):
    c.execute(
        "SELECT rating FROM ratings WHERE username=? AND movie=?",
        (username, movie),
    )
    row = c.fetchone()
    return row[0] if row else None

def get_avg_rating(movie):
    c.execute(
        "SELECT AVG(rating) FROM ratings WHERE movie=?",
        (movie,),
    )
    row = c.fetchone()
    return round(row[0], 2) if row and row[0] is not None else None

@st.cache_data(ttl=3600)
def fetch_person_id(name):
    try:
        url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={name}"
        data = requests.get(url, timeout=10).json()
        results = data.get("results", [])
        if results:
            return results[0].get("id")
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def search_movies(query=None, genre_id=None, cast_id=None):
    try:
        if query:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
        else:
            params = []
            if genre_id:
                params.append(f"with_genres={genre_id}")
            if cast_id:
                
                params.append(f"with_cast={cast_id}")
            tail = "&".join(params)
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}"
            if tail:
                url += "&" + tail
        data = requests.get(url, timeout=10).json()
        return data.get("results", [])[:12]
    except Exception:
        return []

def autocomplete_movies(prefix, limit=5):
    if not prefix:
        return []
    prefix = prefix.lower()
    candidates = []
    for m in get_browsing_movies():
        title = m.get("title", "")
        if title and title.lower().startswith(prefix):
            candidates.append(title)
    return sorted(list(dict.fromkeys(candidates)))[:limit]

def detect_mood_from_text(text):
    t = (text or "").lower()
    if any(k in t for k in ["happy", "funny", "comedy", "laugh"]):
        return "Happy"
    if any(k in t for k in ["bored", "boring"]):
        return "Chill / Relaxed"
    if any(k in t for k in ["romantic", "date night", "love"]):
        return "Romantic"
    if any(k in t for k in ["thriller", "scary", "horror", "suspense"]):
        return "Thriller mood"
    if any(k in t for k in ["sad", "emotional", "cry"]):
        return "Sad"
    if any(k in t for k in ["excited", "action", "adventure"]):
        return "Excited"
    if any(k in t for k in ["relax", "chill", "calm"]):
        return "Chill / Relaxed"
    return "Happy"
def detect_lang_from_text(text):
    t = (text or "").lower()
    if "bollywood" in t or "hindi" in t:
        return "hindi"
    if "tamil" in t:
        return "tamil"
    if "telugu" in t:
        return "telugu"
    return None

@st.cache_data(ttl=3600)
def fetch_watch_providers(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={API_KEY}"
        data = requests.get(url, timeout=10).json()
        return data.get("results", {})
    except Exception:
        return {}

def get_streaming_platforms(movie_title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
        search_data = requests.get(search_url, timeout=10).json()
        if not search_data.get("results"):
            return []
        movie_id = search_data["results"][0]["id"]
        providers = fetch_watch_providers(movie_id)
        region = providers.get("IN") or providers.get("US") or {}
        flatrate = region.get("flatrate", [])
        names = [p.get("provider_name") for p in flatrate if p.get("provider_name")]
        normalized = []
        for n in names:
            if "Netflix" in n:
                normalized.append("Netflix")
            elif "Amazon" in n:
                normalized.append("Prime Video")
            elif "Jio" in n:
                normalized.append("JioHotstar")
        return list(dict.fromkeys(normalized))
    except Exception:
        return []

def ott_search_url(platform, movie_title):
    query = urllib.parse.quote(movie_title or "")
    if platform == "Netflix":
        return f"https://www.netflix.com/search?q={query}"
    if platform == "Prime Video":
        return f"https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}"
    if platform == "JioHotstar":
        return f"https://www.hotstar.com/in/search?q={query}"
    return f"https://www.google.com/search?q={query}+watch+online"

def is_in_theatres(title):
    for m in get_browsing_movies():
        if m.get("title") and m.get("title").lower() == title.lower():
            return True
    return False

def detect_genre_from_text(text):
    t = (text or "").lower()
    genres = {
        "action": ["action", "fight", "battle"],
        "comedy": ["comedy", "funny", "laugh"],
        "thriller": ["thriller", "suspense", "mystery"],
        "romance": ["romance", "romantic", "love"],
        "drama": ["drama", "emotional"],
        "horror": ["horror", "scary"],
        "family": ["family", "kids"],
        "sci-fi": ["sci-fi", "science fiction"],
    }
    for g, keys in genres.items():
        if any(k in t for k in keys):
            return g
    return None

def build_candidate_movies(user_text, username, k=5):
    mood = detect_mood_from_text(user_text)
    lang = detect_lang_from_text(user_text)
    genre = detect_genre_from_text(user_text)
    candidates = get_browsing_movies()
    if lang:
        candidates = [m for m in candidates if normalize_language(m.get("language")) == lang]

    if genre:
        filtered = []
        for m in candidates:
            gnames = []
            if m.get("genre_ids"):
                gnames = [fetch_genre_map().get(gid, "") for gid in m.get("genre_ids", [])]
            elif m.get("genre"):
                gnames = [g.strip() for g in m.get("genre", "").split(",") if g.strip()]
            if any(genre.lower() in g.lower() for g in gnames):
                filtered.append(m)
        if filtered:
            candidates = filtered

    picks = hybrid_recommendations(username, mood, k=k)
    recs = []
    for p in picks:
        platforms = get_streaming_platforms(p.get("title"))
        rating, overview, _ = fetch_details(p.get("title"))
        desc = ""
        if overview:
            desc = overview.split(".")[0].strip() + "."
        recs.append(
            {
                "title": p.get("title"),
                "rating": rating or p.get("rating"),
                "genres": p.get("genres"),
                "platforms": platforms,
                "in_theatres": is_in_theatres(p.get("title", "")),
                "desc": desc,
            }
        )
    return recs

def openai_chat(messages):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "OPENAI_API_KEY not set"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload = {"model": model, "messages": messages, "temperature": 0.7}
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=20,
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, str(e)

@st.cache_resource
def get_gemini_model():
    if not GEMINI_AVAILABLE:
        return None
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    try:
        models = list(genai.list_models())
        # Prefer 1.5 Flash if available for generateContent
        for m in models:
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods and "gemini-1.5-flash" in name:
                return genai.GenerativeModel(name)
        # Fallback to any model that supports generateContent
        for m in models:
            name = getattr(m, "name", "")
            methods = getattr(m, "supported_generation_methods", [])
            if "generateContent" in methods:
                return genai.GenerativeModel(name)
    except Exception:
        pass
    return None

def get_ai_response(user_input, chat_history):
    model = get_gemini_model()
    if model is None:
        return (
            "Gemini is not configured. Please install google-generativeai and set "
            "GEMINI_API_KEY in .env."
        )
    history_text = "\n".join(chat_history[-5:])
    prompt = f"""
You are a friendly movie assistant in a movie booking app.
Talk like a human, not like a robot.
Keep replies short and engaging (2–5 lines).
Suggest movies based on mood, genre, or situation.
Always mention where to watch (Netflix, Prime, JioHotstar, etc).
If the user says hi/hello/hey, greet warmly and ask what they want to watch.
Ask a short follow-up question.

Chat history:
{history_text}

User: {user_input}
AI:
"""
    try:
        response = model.generate_content(prompt)
        return (response.text or "").strip() or "I can help with movie picks. What are you in the mood for?"
    except Exception as e:
        msg = str(e)
        if "429" in msg or "quota" in msg.lower():
            # Friendly rate-limit message
            wait_hint = "Please wait a bit and try again."
            return f"Rate limit reached. {wait_hint}"
        return f"Error: {msg}"

def format_ai_response(user_text, recs):
    system_prompt = (
        "You are a friendly movie assistant. Keep replies short and conversational. "
        "Use at most 3 movies. Format with bullet points and blank lines between bullets. "
        "Each movie must include a 1-sentence description and where to watch. "
        "If in theatres, add: You can also book tickets in theatres from the Book Tickets section. "
        "End with a follow-up question."
    )
    user_prompt = (
        "User message: " + user_text + "\n"
        "Movies list (JSON): " + json.dumps(recs)
    )
    reply, err = openai_chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    if reply:
        return reply
    lines = ["You might enjoy:"]
    for r in recs[:3]:
        platforms = ", ".join(r.get("platforms") or [])
        line = f"• **{r['title']}**"
        if r.get("desc"):
            line += f"\n{r['desc']}"
        if platforms:
            line += f"\nAvailable on: {platforms}"
        if r.get("in_theatres"):
            line += "\nYou can also book tickets in theatres from the Book Tickets section."
        lines.append(line)
        lines.append("")
    lines.append("Would you like something light or intense?")
    return "\n".join(lines)

def recommend_from_history(username, k=8):
    rated = pd.read_sql_query(
        "SELECT movie, rating FROM ratings WHERE username=? ORDER BY rating DESC, created_at DESC LIMIT 1",
        conn,
        params=(username,),
    )
    if not rated.empty:
        base = rated.iloc[0]["movie"]
        names, posters, scores = recommend(base)
        return [{"title": n, "poster": p, "score": s} for n, p, s in zip(names, posters, scores)]

    recent = get_user_recent_movies(username, limit=1)
    if recent:
        base = recent[0]
        names, posters, scores = recommend(base)
        return [{"title": n, "poster": p, "score": s} for n, p, s in zip(names, posters, scores)]
    return []




