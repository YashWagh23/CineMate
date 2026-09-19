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
        if st.button("Enable Notification", key="notify_btn", type="primary", icon=":material/notifications_active:") and notify_movie != "Select":
            st.success(f"Notification enabled for {notify_movie}")

        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                poster = fetch_poster(item)
                rating, overview, release = fetch_details(item)
                render_movie_card(item, poster_url=poster, rating=rating)
                if st.button("Details", key=f"wl_details_{item}", type="secondary", icon=":material/info:", use_container_width=True):
                    st.session_state[f"wl_show_{item}"] = not st.session_state.get(f"wl_show_{item}", False)
                if st.session_state.get(f"wl_show_{item}"):
                    st.write("Release:", release or "Unknown")
                    st.write(overview or "No overview available.")
                if st.button("Remove", key=f"remove_{item}", type="secondary", icon=":material/delete:", use_container_width=True):
                    st.session_state.watchlist.remove(item)
                    st.session_state.pop(f"wl_show_{item}", None)
                    st.success("Removed")
                    st.rerun()
    
    

