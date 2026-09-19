import html
import streamlit as st
import utils
from utils import *
from auth import auth_page, ensure_role_loaded
from home import render_home
from booking import render_booking
from ai_assistant import render_ai_assistant
from watchlist import render_watchlist
from profile import render_profile
from admin import render_admin
import home as home_module
import booking as booking_module

load_css()

st.set_page_config(
    page_title="CineMate - Movie Recommender and Tickets",
    page_icon="assets/logo2.png",
    layout="wide",
)

# Session init
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "watchlist" not in st.session_state: st.session_state.watchlist = []
if "show_details" not in st.session_state: st.session_state.show_details = False
if "remembered_user" not in st.session_state: st.session_state.remembered_user = None
if "role" not in st.session_state: st.session_state.role = "user"

if not st.session_state.logged_in:
    auth_page()
    st.stop()

ensure_role_loaded()

# Sidebar
with st.sidebar:
    render_logo()
    if not API_KEY:
        st.warning("TMDB_API_KEY is not set. Posters, trailers and live movie data are disabled. Add it to your .env file.", icon="⚠️")
    st.markdown("<div class='eyebrow' style='margin-top:8px'>Browse</div>", unsafe_allow_html=True)
    search_term = st.text_input("Search movie", placeholder="Search by title...", label_visibility="collapsed")
    if search_term:
        filtered_movies = movies[movies["title"].str.contains(search_term, case=False, na=False)]
    else:
        filtered_movies = movies
    selected_movie = st.selectbox("Choose Movie", filtered_movies["title"].values)
    utils.selected_movie = selected_movie
    home_module.selected_movie = selected_movie
    booking_module.selected_movie = selected_movie

show_admin = st.session_state.role == "admin"
labels = [
    ":material/home: Home",
    ":material/local_activity: Book Tickets",
    ":material/smart_toy: AI Assistant",
    ":material/bookmark: Watchlist",
    ":material/person: Profile",
]
if show_admin:
    labels.append(":material/admin_panel_settings: Admin")

# Top header: welcome message + logout
top_cols = st.columns([6, 1])
with top_cols[0]:
    st.markdown(
        f"<div style='padding-top:10px;color:var(--muted);font-size:var(--fs-sm);'>"
        f"Welcome back, <b style='color:var(--text)'>{html.escape(st.session_state.username or '')}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )
with top_cols[1]:
    if st.button("", key="top_logout_btn", type="secondary", icon=":material/logout:", help="Log out", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# Tabs routing
tabs = st.tabs(labels)
with tabs[0]:
    render_home()
with tabs[1]:
    render_booking()
with tabs[2]:
    render_ai_assistant()
with tabs[3]:
    render_watchlist()
with tabs[4]:
    render_profile()
if show_admin:
    with tabs[-1]:
        render_admin()
