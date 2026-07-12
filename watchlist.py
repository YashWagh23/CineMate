import streamlit as st
from utils import *


def render_watchlist():
    # tabs index: 0 Home, 1 Book Tickets, 2 AI Assistant, 3 Watchlist, 4 Profile
    st.markdown("<div class='section-title'>Your Watchlist</div>", unsafe_allow_html=True)
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty")
    else:
        sort_choice = st.selectbox(
            "Sort by",
            ["Default", "Rating", "Release Date"],
            key="watchlist_sort",
        )
        items = st.session_state.watchlist[:]
        if sort_choice != "Default":
            scored = []
            for title in items:
                rating, overview, release = fetch_details(title)
                scored.append((title, rating or 0, release or ""))
            if sort_choice == "Rating":
                scored.sort(key=lambda x: x[1], reverse=True)
            else:
                scored.sort(key=lambda x: x[2], reverse=True)
            items = [s[0] for s in scored]
    
        notify_movie = st.selectbox(
            "Notify when available in theatres",
            ["Select"] + items,
            key="watchlist_notify",
        )
        if st.button("Enable Notification", key="notify_btn") and notify_movie != "Select":
            st.success(f"Notification enabled for {notify_movie}")
    
        for item in items:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(item)
            with col2:
                if st.button("Remove", key=f"remove_{item}"):
                    st.session_state.watchlist.remove(item)
                    st.success("Removed")
                    st.rerun()
    
    

