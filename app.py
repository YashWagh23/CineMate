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

st.set_page_config(page_title="CineMate - Movie Recommender and Tickets", page_icon="Movie", layout="wide")

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
    search_term = st.text_input("Search movie")
    if search_term:
        filtered_movies = movies[movies["title"].str.contains(search_term, case=False, na=False)]
    else:
        filtered_movies = movies
    selected_movie = st.selectbox("Choose Movie", filtered_movies["title"].values)
    utils.selected_movie = selected_movie
    home_module.selected_movie = selected_movie
    booking_module.selected_movie = selected_movie

show_admin = st.session_state.role == "admin"
labels = ["Home", "Book Tickets", "AI Assistant", "Watchlist", "Profile"]
if show_admin:
    labels.append("Admin")

# Top-right logout
top_cols = st.columns([8,1])
with top_cols[1]:
    if st.button("Logout", key="top_logout_btn"):
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
