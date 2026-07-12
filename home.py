import streamlit as st
from utils import *

load_css()


def render_home():
    st.markdown("<div class='section-title'>Featured</div>", unsafe_allow_html=True)
    
    rating, overview, release = fetch_details(selected_movie)
    poster_url = fetch_poster(selected_movie)
    
    left, right = st.columns([1, 2])
    with left:
        st.image(poster_url, use_container_width=True)
    with right:
        st.markdown("<div class='hero'>", unsafe_allow_html=True)
        st.subheader(selected_movie)
        st.write("Rating:", rating)
        st.write("Release:", release)
        st.write(overview)
    
        hero_cols = st.columns(4)
        with hero_cols[0]:
            if st.button("Add to Watchlist", key="add_watchlist"):
                if selected_movie not in st.session_state.watchlist:
                    st.session_state.watchlist.append(selected_movie)
                    st.success("Added to watchlist")
                else:
                    st.info("Already in watchlist")
        with hero_cols[1]:
            if st.button("Show Details", key="details_btn"):
                st.session_state.show_details = True
        with hero_cols[2]:
            if st.button("Play Trailer", key="play_trailer"):
                trailer_url = fetch_trailer(selected_movie)
                if trailer_url:
                    vid = get_youtube_id(trailer_url)
                    if vid:
                        st.session_state.show_trailer = True
                        st.session_state.trailer_id = vid
                    else:
                        st.warning("Trailer not available")
                else:
                    st.warning("Trailer not available")
        with hero_cols[3]:
            if st.button("Where to Watch", key="where_watch_btn"):
                query = urllib.parse.quote(f"{selected_movie} where to watch")
                url = f"https://www.google.com/search?q={query}"
                components.html(
                    f"<script>window.open('{url}','_blank');</script>",
                    height=0,
                )
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.get("show_trailer") and st.session_state.get("trailer_id"):
        vid = st.session_state.trailer_id
        st.markdown("<div class='section-title'>Trailer</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <iframe width="100%" height="500"
            src="https://www.youtube.com/embed/{vid}?autoplay=1&mute=1"
            frameborder="0"
            allow="autoplay; encrypted-media"
            allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Close Trailer", key="close_trailer_btn"):
            st.session_state.show_trailer = False
            st.rerun()
    
    if st.session_state.show_details:
        st.markdown("<div class='section-title'>Details</div>", unsafe_allow_html=True)
        st.write("Overview:", overview)
        st.write("Rating:", rating)
        st.write("Release:", release)
    
        full = fetch_movie_full_details(selected_movie)
        if full:
            details = full.get("details", {})
            credits = full.get("credits", {})
            reviews = full.get("reviews", {})
    
            genres = [g.get("name") for g in details.get("genres", []) if g.get("name")]
            runtime = details.get("runtime")
            st.write("Genre:", ", ".join(genres) if genres else "Unknown")
            st.write("Duration:", f"{runtime} min" if runtime else "Unknown")
    
            cast = credits.get("cast", [])
            cast_names = [c.get("name") for c in cast[:8] if c.get("name")]
            if cast_names:
                st.write("Cast:", ", ".join(cast_names))
    
            review_list = reviews.get("results", [])
            if review_list:
                st.markdown("<div class='section-title'>Reviews</div>", unsafe_allow_html=True)
                for rev in review_list[:3]:
                    author = rev.get("author") or "Anonymous"
                    content = rev.get("content") or ""
                    st.write(f"{author}: {content[:300]}{'...' if len(content) > 300 else ''}")
    
    st.markdown("<div class='section-title'>Rate This Movie</div>", unsafe_allow_html=True)
    avg_rating = get_avg_rating(selected_movie)
    st.write("Community Rating:", avg_rating if avg_rating is not None else "No ratings yet")
    current_rating = get_user_rating(st.session_state.username, selected_movie)
    rating_options = [1, 2, 3, 4, 5]
    default_idx = rating_options.index(current_rating) if current_rating in rating_options else 3
    user_rating = st.radio(
        "Your Rating",
        rating_options,
        index=default_idx,
        horizontal=True,
        key=f"rate_{selected_movie}",
    )
    if st.button("Submit Rating", key="submit_rating_btn"):
        upsert_rating(st.session_state.username, selected_movie, int(user_rating))
        st.success("Rating saved")
    
    st.markdown("<div class='section-title'>How are you feeling today?</div>", unsafe_allow_html=True)
    emoji_mood = st.radio(
        "Mood",
        ["😊 Happy", "😢 Sad", "😍 Romantic", "😴 Relaxed", "🔥 Excited", "😱 Thriller"],
        horizontal=True,
    )
    mood_map = {
        "😊 Happy": "Happy",
        "😢 Sad": "Sad",
        "😍 Romantic": "Romantic",
        "😴 Relaxed": "Chill / Relaxed",
        "🔥 Excited": "Excited",
        "😱 Thriller": "Thriller mood",
    }
    selected_mood = mood_map.get(emoji_mood, "Happy")
    
    st.markdown("<div class='section-title'>Mood-Based Picks</div>", unsafe_allow_html=True)
    mood_options = [
        "Happy",
        "Sad",
        "Romantic",
        "Excited",
        "Thriller mood",
        "Chill / Relaxed",
    ]
    selected_mood = st.selectbox("Select your mood", mood_options, index=mood_options.index(selected_mood))
    if st.button("Get Mood Recommendations", key="mood_reco_btn"):
        recs = recommend_by_mood(selected_mood, st.session_state.username)
        if not recs:
            st.warning("No mood recommendations available")
        else:
            cols = st.columns(4)
            for i, rec in enumerate(recs):
                with cols[i % 4]:
                    if rec.get("poster"):
                        st.image(rec["poster"], use_container_width=True)
                    st.caption(rec.get("title", ""))
                    st.write("Rating:", rec.get("rating"))
                    genre_map = fetch_genre_map()
                    genres = [genre_map.get(gid, "") for gid in rec.get("genre_ids", [])]
                    genres = [g for g in genres if g]
                    if genres:
                        st.write("Genres:", ", ".join(genres[:3]))
    
    st.markdown("<div class='section-title'>Hybrid Recommendations</div>", unsafe_allow_html=True)
    if st.button("Generate Hybrid Picks", key="hybrid_reco_btn"):
        hybrid = hybrid_recommendations(st.session_state.username, selected_mood, k=10)
        if not hybrid:
            st.warning("No hybrid recommendations available")
        else:
            cols = st.columns(5)
            for i, rec in enumerate(hybrid):
                with cols[i % 5]:
                    if rec.get("poster"):
                        st.image(rec["poster"], use_container_width=True)
                    st.caption(rec.get("title", ""))
                    if rec.get("rating") is not None:
                        st.write("Rating:", rec.get("rating"))
                    if rec.get("genres"):
                        st.write("Genres:", ", ".join(rec["genres"][:3]))
    
    st.markdown("<div class='section-title'>Personalized For You</div>", unsafe_allow_html=True)
    personalized = recommend_from_history(st.session_state.username)
    if not personalized:
        st.info("Rate or book a movie to get personalized picks")
    else:
        cols = st.columns(4)
        for i, rec in enumerate(personalized[:8]):
            with cols[i % 4]:
                if rec.get("poster"):
                    st.image(rec["poster"], use_container_width=True)
                st.caption(rec.get("title", ""))
                st.write("Match:", rec.get("score"))
    
    st.markdown("<div class='section-title'>Search Movies</div>", unsafe_allow_html=True)
    query = st.text_input("Search by movie name")
    if query:
        suggestions = autocomplete_movies(query)
        if suggestions:
            choice = st.selectbox("Suggestions", suggestions)
            if st.button("Use Suggestion", key="use_suggestion"):
                query = choice
    actor = st.text_input("Search by actor")
    genre_map = fetch_genre_map()
    genre_options = ["Any"] + sorted(genre_map.values())
    genre_choice = st.selectbox("Filter by genre", genre_options)
    if st.button("Search", key="search_btn"):
        genre_id = None
        if genre_choice != "Any":
            for gid, gname in genre_map.items():
                if gname == genre_choice:
                    genre_id = gid
                    break
        cast_id = fetch_person_id(actor) if actor else None
        results = search_movies(query=query or None, genre_id=genre_id, cast_id=cast_id)
        if not results:
            st.warning("No results found")
        else:
            cols = st.columns(4)
            for i, movie in enumerate(results):
                with cols[i % 4]:
                    if movie.get("poster_path"):
                        st.image(
                            "https://image.tmdb.org/t/p/w500" + movie["poster_path"],
                            use_container_width=True,
                        )
                    st.caption(movie.get("title", ""))
                    st.write("Rating:", movie.get("vote_average"))
                    genres = [genre_map.get(gid, "") for gid in movie.get("genre_ids", [])]
                    genres = [g for g in genres if g]
                    if genres:
                        st.write("Genres:", ", ".join(genres[:3]))
    
    st.markdown("<div class='section-title'>Browse Movies</div>", unsafe_allow_html=True)
    lang_filter = st.radio(
        "Filter",
        ["All Movies", "Hollywood", "Bollywood", "South Indian"],
        horizontal=True,
        key="language_filter",
    )
    browse_list = apply_language_filter(get_browsing_movies(), lang_filter)
    if not browse_list:
        st.warning("No movies found for this filter")
    else:
        cols = st.columns(4)
        for i, movie in enumerate(browse_list[:12]):
            with cols[i % 4]:
                poster = movie.get("poster_url")
                if not poster and movie.get("poster_path"):
                    poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
                if not poster and movie.get("title"):
                    poster = fetch_poster(movie.get("title"))
                if poster:
                    st.image(poster, use_container_width=True)
                st.caption(movie.get("title", ""))
                rating_val = movie.get("vote_average", movie.get("rating"))
                st.write("Rating:", rating_val)
                genres = []
                if movie.get("genre_ids"):
                    genres = [genre_map.get(gid, "") for gid in movie.get("genre_ids", [])]
                elif movie.get("genre"):
                    genres = [g.strip() for g in movie.get("genre", "").split(",") if g.strip()]
                if genres:
                    st.write("Genre:", ", ".join(genres[:3]))
    
    st.markdown("<div class='section-title'>Trending This Week</div>", unsafe_allow_html=True)
    trending_movies = fetch_trending_movies()
    if not trending_movies:
        st.warning("Trending movies unavailable right now")
    else:
        cols = st.columns(5)
        for i, movie in enumerate(trending_movies[:5]):
            with cols[i]:
                if movie.get("poster_path"):
                    st.image(
                        "https://image.tmdb.org/t/p/w500" + movie["poster_path"],
                        use_container_width=True,
                    )
                st.caption(movie.get("title", ""))
                tags = [("Trending", "tag-amber")]
                for t, cls in tags:
                    st.markdown(f"<span class='tag {cls}'>{t}</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Because You Watched</div>", unsafe_allow_html=True)
    if st.button("Recommend", key="recommend_btn"):
        with st.spinner("Finding best movies for you..."):
            names, posters, scores = recommend(selected_movie)
        if not names:
            st.warning("No recommendations found")
        else:
            cols = st.columns(5)
            for i in range(len(names)):
                with cols[i]:
                    st.text(names[i])
                    st.image(posters[i], use_container_width=True)
                    st.caption(f"Match: {scores[i]}%")
                    st.markdown("<span class='tag tag-red'>Recommended</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Coming Soon</div>", unsafe_allow_html=True)
    coming = get_coming_soon_movies()
    if not coming:
        st.info("No coming soon titles yet")
    else:
        cols = st.columns(5)
        for i, movie in enumerate(coming[:5]):
            with cols[i % 5]:
                poster = movie.get("poster_url") or fetch_poster(movie.get("title"))
                if poster:
                    st.image(poster, use_container_width=True)
                st.caption(movie.get("title", ""))
                st.markdown("<span class='tag tag-blue'>New</span>", unsafe_allow_html=True)
                if movie.get("release_date"):
                    st.write("Release:", movie.get("release_date"))
                if st.button("Add to Watchlist", key=f"coming_watch_{movie.get('title')}"):
                    if movie.get("title") not in st.session_state.watchlist:
                        st.session_state.watchlist.append(movie.get("title"))
                        st.markdown("<div class='toast'>Added to watchlist</div>", unsafe_allow_html=True)
                if st.button("Watch Trailer", key=f"coming_trailer_{movie.get('title')}"):
                    trailer_url = fetch_trailer(movie.get("title"))
                    if trailer_url:
                        st.video(trailer_url)
                    else:
                        st.warning("Trailer not available")
    
    

