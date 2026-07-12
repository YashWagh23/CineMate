import streamlit as st
from utils import *


def render_admin():
    if show_admin:
        st.markdown("<div class='section-title'>Admin Dashboard</div>", unsafe_allow_html=True)
    
        tab1, tab2, tab3, tab4 = st.tabs(["Users", "Bookings", "Movies", "Theatres"])
    
        with tab1:
            users_df = pd.read_sql_query("SELECT username, role FROM users", conn)
            st.dataframe(users_df, use_container_width=True)
    
        with tab2:
            bookings_df = pd.read_sql_query("SELECT * FROM bookings", conn)
            st.dataframe(bookings_df, use_container_width=True)
    
        with tab3:
            st.markdown("<div class='section-title'>Add Movie</div>", unsafe_allow_html=True)
            with st.form("admin_add_movie"):
                title = st.text_input("Title")
                rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
                genre = st.text_input("Genre (comma separated)")
                poster_url = st.text_input("Poster URL (optional)")
                language = st.selectbox("Language", ["english", "hindi", "tamil", "telugu"])
                is_running = st.checkbox("Currently Running", value=True)
                submitted = st.form_submit_button("Add Movie")
            if submitted:
                if not title:
                    st.warning("Title is required")
                else:
                    try:
                        c.execute(
                            "INSERT INTO admin_movies (title, rating, genre, poster_url, language, is_running) VALUES (?,?,?,?,?,?)",
                            (title, rating, genre, poster_url, language, 1 if is_running else 0),
                        )
                        conn.commit()
                        st.success("Movie added")
                    except Exception:
                        st.warning("Movie already exists")
    
            st.markdown("<div class='section-title'>Remove Movie</div>", unsafe_allow_html=True)
            c.execute("SELECT title FROM admin_movies ORDER BY title")
            titles = [r[0] for r in c.fetchall()]
            if titles:
                to_remove = st.selectbox("Select Movie", titles, key="remove_movie")
                if st.button("Remove Selected Movie"):
                    c.execute("DELETE FROM admin_movies WHERE title=?", (to_remove,))
                    conn.commit()
                    st.success("Movie removed")
            else:
                st.info("No admin movies yet")
    
        with tab4:
            st.markdown("<div class='section-title'>Add Theatre Showtime</div>", unsafe_allow_html=True)
            with st.form("admin_add_theatre"):
                city = st.text_input("City")
                theatre = st.text_input("Theatre Name")
                show_time = st.text_input("Show Time (e.g., 6:30 PM)")
                submitted = st.form_submit_button("Add Showtime")
            if submitted:
                if not city or not theatre or not show_time:
                    st.warning("City, Theatre, and Show Time are required")
                else:
                    c.execute(
                        "INSERT INTO theatres (city, theatre, show_time) VALUES (?,?,?)",
                        (city, theatre, show_time),
                    )
                    conn.commit()
                    st.success("Showtime added")
    
            st.markdown("<div class='section-title'>Remove Showtime</div>", unsafe_allow_html=True)
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
            else:
                st.info("No showtimes added yet")
    
    
    
    
    

