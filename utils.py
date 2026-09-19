import base64
import hashlib
import html
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
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Manrope:wght@400;500;600;700;800&display=swap');

/* ============ DESIGN TOKENS ============ */
:root {
    /* surfaces */
    --bg: #0a0a0d;
    --bg-elevated: #111114;
    --surface: #16161b;
    --surface-2: #1d1d23;
    --border: rgba(255,255,255,0.09);
    --border-strong: rgba(255,255,255,0.18);
    /* text */
    --text: #f3f2ef;
    --muted: #9b9ba6;
    --muted-2: #6f6f7a;
    /* brand */
    --accent: #e11d2e;
    --accent-hover: #ff2f3f;
    --accent-soft: rgba(225,29,46,0.14);
    --accent-border: rgba(225,29,46,0.4);
    --gold: #f0b93d;
    --success: #34c98e;
    /* legacy alias used by a few older inline styles */
    --card: var(--surface);
    --line: var(--border);
    /* radius scale (shape lock: pills for actions, lg for cards, md for inputs) */
    --r-sm: 8px;
    --r-md: 12px;
    --r-lg: 18px;
    --r-pill: 999px;
    /* spacing (8pt) */
    --sp-1: 4px; --sp-2: 8px; --sp-3: 12px; --sp-4: 16px;
    --sp-5: 24px; --sp-6: 32px; --sp-7: 48px; --sp-8: 64px;
    /* type scale, 1.25 ratio off a 16px base */
    --fs-xs: 0.75rem; --fs-sm: 0.875rem; --fs-base: 1rem;
    --fs-md: 1.125rem; --fs-lg: 1.375rem; --fs-xl: 1.75rem;
    --fs-2xl: 2.25rem; --fs-3xl: 3rem;
    --font-display: 'Bebas Neue', 'Manrope', sans-serif;
    --font-body: 'Manrope', 'Segoe UI', sans-serif;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        transition-duration: 0.001ms !important;
        scroll-behavior: auto !important;
    }
}

html, body, [class*="css"] {
    font-family: var(--font-body);
}
.stApp {
    background:
        radial-gradient(1100px 700px at 15% -10%, rgba(225,29,46,0.10) 0%, transparent 55%),
        var(--bg);
    color: var(--text);
    font-family: var(--font-body);
}
.stApp, .stApp * { scrollbar-color: var(--border-strong) transparent; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: var(--r-pill); }
::-webkit-scrollbar-track { background: transparent; }

@keyframes fadein {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.block-container { animation: fadein 0.35s ease-out; }

/* focus-visible ring for keyboard users, everywhere */
button:focus-visible, a:focus-visible, input:focus-visible,
[data-testid="stCheckbox"] label:focus-within {
    outline: 2px solid var(--accent) !important;
    outline-offset: 2px !important;
}

/* ============ TYPOGRAPHY ============ */
.section-title {
    font-family: var(--font-body);
    font-size: var(--fs-lg);
    font-weight: 800;
    letter-spacing: -0.01em;
    color: var(--text);
    margin: var(--sp-6) 0 var(--sp-3) 0;
}
.eyebrow {
    display: block;
    font-family: var(--font-body);
    font-size: var(--fs-xs);
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: var(--sp-2);
}
.brand-word {
    font-family: var(--font-display);
    font-size: var(--fs-2xl);
    letter-spacing: 0.03em;
    color: var(--text);
    line-height: 1;
}
.brand-word .accent { color: var(--accent); }

/* ============ CARDS / CONTAINERS ============ */
.card, .hero, .booking-card, .summary-card, .theatre-card, .ticket-card,
.profile-card, .payment-card, .admin-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
}
.card, .booking-card, .profile-card, .payment-card { padding: var(--sp-4); }
.card:hover {
    border-color: var(--border-strong);
    box-shadow: 0 16px 36px rgba(0,0,0,0.35);
}
.hero {
    background: linear-gradient(135deg, rgba(225,29,46,0.16), rgba(225,29,46,0.02) 60%);
    padding: var(--sp-6);
}
/* Empty markdown div "cards" (an unclosed-div hack that doesn't actually wrap
   Streamlit widgets) collapse to a stray decorative bar; hide them instead. */
.card:empty, .hero:empty, .booking-card:empty, .profile-card:empty,
.payment-card:empty, .ticket-card:empty, .summary-card:empty,
.admin-card:empty, .theatre-card:empty {
    display: none;
}
/* Native Streamlit bordered containers, restyled to match the app theme */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"]) {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: var(--sp-1);
}

/* ============ BUTTONS (primary vs secondary hierarchy) ============ */
.stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
    font-family: var(--font-body) !important;
    border-radius: var(--r-pill) !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 700 !important;
    font-size: var(--fs-sm) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, border-color 0.15s ease !important;
    border: 1px solid transparent !important;
}
.stButton>button:active, .stFormSubmitButton>button:active, .stDownloadButton>button:active {
    transform: scale(0.98) !important;
}
/* primary: the one loud action */
.stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"],
.stDownloadButton>button[kind="primary"] {
    background: var(--accent) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 20px rgba(225,29,46,0.28) !important;
}
.stButton>button[kind="primary"]:hover, .stFormSubmitButton>button[kind="primary"]:hover,
.stDownloadButton>button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 10px 26px rgba(225,29,46,0.4) !important;
}
/* secondary: everything else, quiet by default */
.stButton>button[kind="secondary"], .stFormSubmitButton>button[kind="secondary"],
.stDownloadButton>button[kind="secondary"] {
    background: transparent !important;
    color: var(--text) !important;
    border: 1px solid var(--border-strong) !important;
}
.stButton>button[kind="secondary"]:hover, .stFormSubmitButton>button[kind="secondary"]:hover,
.stDownloadButton>button[kind="secondary"]:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.stButton>button:disabled {
    opacity: 0.4 !important;
    box-shadow: none !important;
}
.link-btn {
    display: inline-block;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: var(--r-pill);
    background: var(--accent);
    color: #ffffff;
    font-weight: 700;
    font-size: var(--fs-sm);
    transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}
.link-btn:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(225,29,46,0.35);
}

/* ============ SIDEBAR ============ */
section[data-testid="stSidebar"] {
    background: var(--bg-elevated);
    color: var(--text);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: var(--fs-xs) !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    font-weight: 700 !important;
}

/* ============ IMAGES ============ */
.stImage img {
    border-radius: var(--r-md);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stImage img:hover {
    transform: scale(1.02);
    box-shadow: 0 16px 34px rgba(0,0,0,0.45);
}

/* ============ FORMS / INPUTS ============ */
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stTextArea>div>textarea,
.stDateInput input,
.stNumberInput input {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
}
.stTextInput>div>div>input:focus,
.stSelectbox>div[data-baseweb="select"]:focus-within>div,
.stTextArea>div>textarea:focus {
    border: 1px solid var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
    outline: none !important;
}
.stTextInput label, .stSelectbox label, .stTextArea label, .stRadio label,
.stDateInput label, .stNumberInput label, .stFileUploader label {
    font-weight: 700 !important;
    color: var(--text) !important;
}
[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: var(--sp-5) !important;
}

/* ============ MOVIE CARD ============ */
.movie-card { margin-bottom: var(--sp-2); }
.movie-card-media {
    position: relative;
    aspect-ratio: 2 / 3;
    width: 100%;
    overflow: hidden;
    border-radius: var(--r-lg);
    background: var(--surface-2);
    border: 1px solid var(--border);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
}
.movie-card-media img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.35s ease;
}
.movie-card:hover .movie-card-media img { transform: scale(1.08); }
.movie-card:hover .movie-card-media {
    border-color: var(--border-strong);
    box-shadow: 0 18px 40px rgba(0,0,0,0.5);
}
.movie-card-scrim {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.15) 55%, transparent 75%);
}
.movie-card-title {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    padding: var(--sp-3);
    color: #ffffff;
    font-weight: 800;
    font-size: var(--fs-sm);
    line-height: 1.25;
    text-shadow: 0 2px 6px rgba(0,0,0,0.6);
}
.movie-card-badge {
    position: absolute;
    top: var(--sp-2);
    right: var(--sp-2);
    background: rgba(10,10,13,0.72);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.18);
    color: var(--gold);
    font-weight: 800;
    font-size: var(--fs-xs);
    padding: 3px 8px;
    border-radius: var(--r-pill);
}
.movie-card-tag {
    position: absolute;
    top: var(--sp-2);
    left: var(--sp-2);
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: var(--r-pill);
}

/* ============ SEATS ============ */
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
    height: 34px;
    border-radius: var(--r-sm);
    border: 1px solid var(--border);
    font-weight: 700;
    font-size: var(--fs-sm);
    background: var(--surface-2);
    color: var(--text);
    cursor: pointer;
    margin-bottom: 6px;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, border-color .15s ease;
}
.seat-grid [data-testid="stCheckbox"] label:hover {
    transform: translateY(-2px);
    border-color: var(--border-strong);
    box-shadow: 0 6px 18px rgba(0,0,0,0.3);
}
.seat-grid [data-testid="stCheckbox"] input[type="checkbox"] {
    display: none;
}
.seat-grid [data-testid="stCheckbox"] label:has(input:checked) {
    background: var(--accent);
    border-color: var(--accent);
    color: #ffffff;
}
.seat-grid [data-testid="stCheckbox"] label:has(input:disabled) {
    background: rgba(255,255,255,0.03);
    color: var(--muted-2);
    border-style: dashed;
    cursor: not-allowed;
}
.seat-row-label {
    font-weight: 800;
    color: var(--muted);
    padding-top: 8px;
}
.seat-tier-legend {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--r-pill);
    border: 1px solid var(--border);
    margin-right: var(--sp-2);
    font-size: var(--fs-xs);
    font-weight: 700;
    color: var(--muted);
}
.tier-gold { border-color: rgba(240,185,61,0.5); color: var(--gold); }
.tier-silver { border-color: var(--border-strong); color: var(--text); }
.tier-regular { border-color: var(--border); color: var(--muted); }
@media (max-width: 768px) {
    .seat-grid [data-testid="stCheckbox"] label {
        width: 34px;
        height: 28px;
        font-size: 0.7rem;
    }
}

/* ============ BOOKING FLOW ============ */
.booking-steps {
    display: flex;
    gap: var(--sp-2);
    flex-wrap: wrap;
    margin-bottom: var(--sp-4);
}
.booking-step {
    padding: 6px 14px;
    border-radius: var(--r-pill);
    border: 1px solid var(--border);
    background: var(--surface);
    font-size: var(--fs-xs);
    font-weight: 700;
    color: var(--muted);
}
.summary-card { padding: var(--sp-5); position: sticky; top: var(--sp-4); }
.pill {
    display: inline-block;
    padding: 6px 14px;
    border-radius: var(--r-pill);
    border: 1px solid var(--border);
    margin: 4px 6px 4px 0;
    background: var(--surface);
    font-size: var(--fs-sm);
}
.pill-active { background: var(--accent-soft); border-color: var(--accent-border); color: var(--text); }
.theatre-card { padding: var(--sp-3); transition: box-shadow .2s ease, border-color .2s ease; }
.theatre-card.pill-active { background: var(--accent-soft); border-color: var(--accent-border); }
.theatre-card:hover { box-shadow: 0 10px 24px rgba(0,0,0,0.3); }
.ticket-card { padding: var(--sp-5); }

/* ============ PROFILE ============ */
.avatar-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: var(--accent-soft);
    border: 1px solid var(--accent-border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-display);
    font-size: var(--fs-2xl);
    letter-spacing: 0.04em;
    color: var(--text);
    margin-bottom: var(--sp-3);
}
.profile-label {
    color: var(--muted);
    font-size: var(--fs-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    margin-top: var(--sp-3);
}
.profile-value {
    font-size: var(--fs-md);
    font-weight: 700;
    color: var(--text);
    margin-bottom: var(--sp-1);
}

/* ============ AI CHAT ============ */
.chat-wrap {
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: var(--sp-4);
    background: var(--surface);
    max-height: 520px;
    overflow-y: auto;
}
.bubble {
    padding: 10px 14px;
    border-radius: var(--r-lg);
    margin: var(--sp-2) 0;
    max-width: 80%;
    font-size: var(--fs-sm);
    line-height: 1.5;
}
.bubble.user {
    background: var(--accent);
    color: #ffffff;
    margin-left: auto;
    border-bottom-right-radius: var(--r-sm);
}
.bubble.ai {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-bottom-left-radius: var(--r-sm);
}
.msg-row { display: flex; }
.msg-row.user { justify-content: flex-end; }
.msg-row.ai { justify-content: flex-start; }

/* ============ TABS (top nav) ============ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-pill);
    padding: 5px;
    width: fit-content;
    max-width: 100%;
    overflow-x: auto;
    margin: var(--sp-2) 0 var(--sp-6) 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    font-size: var(--fs-sm) !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    padding: 10px 20px !important;
    border-radius: var(--r-pill) !important;
    transition: color .15s ease, background .15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: rgba(255,255,255,0.05);
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    background: var(--accent) !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 16px rgba(225,29,46,0.3);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* ============ AUTH SCREEN ============ */
.logo-link img {
    height: 52px;
    transition: transform 0.2s ease, filter 0.2s ease;
}
.logo-link img:hover {
    transform: scale(1.03);
    filter: drop-shadow(0 0 6px rgba(225,29,46,0.5));
}
.auth-card {
    background: rgba(10,10,13,0.78);
    backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--r-lg);
    padding: var(--sp-6);
    box-shadow: 0 24px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06);
}

/* ============ ADMIN ============ */
.admin-card { padding: var(--sp-4); }
.admin-kpi {
    font-family: var(--font-display);
    font-size: var(--fs-2xl);
    letter-spacing: 0.02em;
    color: var(--text);
}
.admin-label {
    color: var(--muted);
    font-size: var(--fs-sm);
    font-weight: 600;
}
.admin-nav-title {
    font-weight: 800;
    margin-bottom: var(--sp-2);
    color: var(--muted);
    text-transform: uppercase;
    font-size: var(--fs-xs);
    letter-spacing: 0.08em;
}

/* ============ TAGS / BADGES ============ */
.tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: var(--r-pill);
    font-size: 0.7rem;
    font-weight: 700;
    border: 1px solid var(--border);
    margin-right: 6px;
    background: var(--surface);
    color: var(--muted);
}
.tag-green { color: var(--success); border-color: rgba(52,201,142,0.4); background: rgba(52,201,142,0.1); }
.tag-blue { color: #6fb3ff; border-color: rgba(111,179,255,0.4); background: rgba(111,179,255,0.1); }
.tag-amber { color: var(--gold); border-color: rgba(240,185,61,0.4); background: rgba(240,185,61,0.1); }
.tag-red { color: var(--accent-hover); border-color: var(--accent-border); background: var(--accent-soft); }

/* ============ MISC ============ */
.skeleton {
    height: 180px;
    border-radius: var(--r-lg);
    background: linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.10), rgba(255,255,255,0.04));
    background-size: 200% 100%;
    animation: shimmer 1.2s infinite;
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
.toast {
    padding: 10px 14px;
    border-radius: var(--r-md);
    background: rgba(52,201,142,0.14);
    color: #bdf5e0;
    border: 1px solid rgba(52,201,142,0.4);
    margin-bottom: var(--sp-2);
}
.tooltip-seat { position: relative; cursor: pointer; }
.tooltip-seat:hover::after {
    content: "Select seat";
    position: absolute;
    top: -28px;
    left: 0;
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 4px 8px;
    border-radius: var(--r-sm);
    font-size: 0.7rem;
}
.booking-history-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    padding: var(--sp-4);
    margin-bottom: var(--sp-3);
    display: flex;
    justify-content: space-between;
    gap: var(--sp-4);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color .2s ease;
}
.booking-history-card:hover {
    border-color: var(--border-strong);
    box-shadow: 0 14px 32px rgba(0,0,0,0.4);
}
.bh-title { font-size: var(--fs-md); font-weight: 800; color: var(--text); margin-bottom: var(--sp-1); }
.bh-sub { color: var(--muted); font-size: var(--fs-sm); margin-bottom: 4px; }
.bh-seat {
    display: inline-block;
    padding: 4px 10px;
    border-radius: var(--r-pill);
    background: var(--accent-soft);
    color: var(--text);
    border: 1px solid var(--accent-border);
    font-size: var(--fs-sm);
    margin-bottom: 6px;
}
.bh-id { color: var(--muted-2); font-size: var(--fs-xs); }
</style>
""",
        unsafe_allow_html=True
    )


def render_movie_card(title, poster_url=None, rating=None, tag=None, tag_class="tag-red"):
    safe_title = html.escape(title or "Untitled")
    poster = poster_url or "https://placehold.co/500x750/16161b/6f6f7a?text=No+Poster"
    badge_html = ""
    if rating not in (None, ""):
        try:
            badge_html = f'<div class="movie-card-badge">&#9733; {float(rating):.1f}</div>'
        except (TypeError, ValueError):
            badge_html = ""
    tag_html = f'<span class="movie-card-tag {tag_class}">{html.escape(str(tag))}</span>' if tag else ""
    st.markdown(
        f"""
        <div class="movie-card">
            <div class="movie-card-media">
                <img src="{poster}" alt="{safe_title}" loading="lazy" />
                {badge_html}
                {tag_html}
                <div class="movie-card-scrim"></div>
                <div class="movie-card-title">{safe_title}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
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

API_KEY = os.getenv("TMDB_API_KEY", "")

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
    return "https://placehold.co/500x750/141414/f5f5f5?text=No+Poster"

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

    if not smtp_host or not smtp_user or not smtp_pass or not to_email:
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




