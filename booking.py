import streamlit as st
from utils import *

load_css()


def render_booking():
    st.markdown("<div class='section-title'>Book Movie Tickets</div>", unsafe_allow_html=True)
    
    if "booking_theatre" not in st.session_state:
        st.session_state.booking_theatre = None
    if "booking_time" not in st.session_state:
        st.session_state.booking_time = None
    if "booking_movie" not in st.session_state:
        st.session_state.booking_movie = None
    if "booking_step" not in st.session_state:
        st.session_state.booking_step = "select"
    if "pending_booking" not in st.session_state:
        st.session_state.pending_booking = None
    if "last_booking" not in st.session_state:
        st.session_state.last_booking = None
    
    genre_map = fetch_genre_map()
    browsing_all = get_browsing_movies()
    now_playing = [
        m
        for m in browsing_all
        if normalize_language(m.get("language")) in ("english", "hindi")
    ]
    now_playing.sort(
        key=lambda m: m.get("vote_average", m.get("rating", 0)) or 0, reverse=True
    )
    now_titles = [m.get("title", "") for m in now_playing if m.get("title")]
    
    st.markdown(
        "<div class='booking-steps'>"
        "<span class='booking-step'>1. Select Movie</span>"
        "<span class='booking-step'>2. Select City</span>"
        "<span class='booking-step'>3. Select Theatre</span>"
        "<span class='booking-step'>4. Select Date & Time</span>"
        "<span class='booking-step'>5. Select Seats</span>"
        "<span class='booking-step'>6. Confirm Booking</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    left, right = st.columns([7, 3])
    
    with left:
        st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Now Playing</div>", unsafe_allow_html=True)
        if not now_titles:
            st.warning("No movies available right now")
            movie_choice = selected_movie
        else:
            cols = st.columns(4)
            for i, movie in enumerate(now_playing[:8]):
                with cols[i % 4]:
                    poster = movie.get("poster_url")
                    if not poster and movie.get("poster_path"):
                        poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
                    if not poster and movie.get("title"):
                        poster = fetch_poster(movie.get("title"))
                    title = movie.get("title", "")
                    is_selected = st.session_state.booking_movie == title
                    render_movie_card(
                        title, poster,
                        rating=movie.get("vote_average", movie.get("rating")),
                        tag="Selected" if is_selected else None,
                        tag_class="tag-green",
                    )
                    btn_label = "Selected" if is_selected else "Select"
                    if st.button(
                        btn_label, key=f"pick_{title}", use_container_width=True,
                        type="primary" if is_selected else "secondary",
                        icon=":material/check_circle:" if is_selected else None,
                    ):
                        st.session_state.booking_movie = title
                        st.rerun()
            if st.session_state.booking_movie is None:
                st.session_state.booking_movie = now_titles[0]
            movie_choice = st.session_state.booking_movie
    
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
        content_left, content_right = st.columns([1, 2])
    
        with content_left:
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            poster = fetch_poster(movie_choice) if movie_choice else None
            if poster:
                st.image(poster, width=200)
            st.markdown(f"**{movie_choice}**")
            movie_details = next(
                (m for m in now_playing if m.get("title") == movie_choice), None
            )
            if movie_details:
                rating_val = movie_details.get("vote_average", movie_details.get("rating"))
                if rating_val is not None:
                    st.write("Rating:", rating_val)
                genres = []
                if movie_details.get("genre_ids"):
                    genres = [genre_map.get(gid, "") for gid in movie_details.get("genre_ids", [])]
                elif movie_details.get("genre"):
                    genres = [g.strip() for g in movie_details.get("genre", "").split(",") if g.strip()]
                if genres:
                    st.write("Genre:", ", ".join(genres[:3]))
            st.markdown("</div>", unsafe_allow_html=True)
    
        with content_right:
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Select City / Location</div>", unsafe_allow_html=True)
            theatres_live = fetch_theatres_from_db()
            if not theatres_live:
                theatres_live = default_theatres_by_city
            city = st.selectbox("City", list(theatres_live.keys()))
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
            show_date = st.session_state.get("booking_date", date.today())
    
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Select Theatre</div>", unsafe_allow_html=True)
            theatre_options = list(theatres_live[city].keys())
            if st.session_state.booking_theatre not in theatre_options:
                st.session_state.booking_theatre = theatre_options[0]
            cols = st.columns(2)
            for i, th in enumerate(theatre_options):
                with cols[i % 2]:
                    active_class = "theatre-card pill-active" if th == st.session_state.booking_theatre else "theatre-card"
                    avail, tag = theatre_availability(
                        movie_choice, city, th, theatres_live[city][th][0], show_date
                    )
                    tag_color = "#ef4444" if tag == "Almost Full" else "#f59e0b" if tag == "Fast Filling" else "#22c55e"
                    st.markdown(
                        f"<div class='{active_class}'>"
                        f"<div>{th}</div>"
                        f"<div style='font-size:0.85rem;color:#cbd5f5'>Seats Available: {avail}</div>"
                        f"<div style='font-size:0.75rem;color:{tag_color}'>{tag}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    is_active_theatre = th == st.session_state.booking_theatre
                    if st.button(
                        "Selected" if is_active_theatre else "Choose",
                        key=f"choose_theatre_{th}",
                        type="primary" if is_active_theatre else "secondary",
                        icon=":material/check_circle:" if is_active_theatre else None,
                        use_container_width=True,
                    ):
                        st.session_state.booking_theatre = th
                        st.rerun()
            theatre = st.session_state.booking_theatre or theatre_options[0]
            st.markdown(f"Selected Theatre: {theatre}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Select Date & Show Time</div>", unsafe_allow_html=True)
            show_date = st.date_input("Date", min_value=date.today())
            st.session_state.booking_date = show_date
            show_times = theatres_live[city][theatre]
            if st.session_state.booking_time not in show_times:
                st.session_state.booking_time = show_times[0]
            st.write("Show Times")
            time_cols = st.columns(2)
            for i, t in enumerate(show_times):
                with time_cols[i % 2]:
                    active = st.session_state.booking_time == t
                    if st.button(
                        t, key=f"time_{t}", use_container_width=True,
                        type="primary" if active else "secondary",
                        icon=":material/check:" if active else None,
                    ):
                        st.session_state.booking_time = t
                        st.rerun()
            show_time = st.session_state.booking_time or show_times[0]
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Select Seats</div>", unsafe_allow_html=True)
            selected_seats = []
            show_key = f"{movie_choice}_{city}_{theatre}_{show_time}_{show_date}"
            c.execute(
                "SELECT seats FROM bookings WHERE movie=? AND city=? AND theatre=? AND show_time=? AND show_date=?",
                (movie_choice, city, theatre, show_time, str(show_date)),
            )
            booked = set()
            for row in c.fetchall():
                if row[0]:
                    booked.update([s.strip() for s in row[0].split(",") if s.strip()])
            lock_map = get_lock_map(movie_choice, city, theatre, show_time, str(show_date))
            locked_seats = set(lock_map.keys())
            booked.update(locked_seats)
    
            st.markdown(
                "<span class='legend-dot' style='background:#22c55e'></span>Available "
                "<span class='legend-dot' style='background:#60a5fa;margin-left:12px'></span>Selected "
                "<span class='legend-dot' style='background:#ef4444;margin-left:12px'></span>Booked",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div style='margin-top:6px'>"
                "<span class='seat-tier-legend tier-gold'>Gold - 350</span>"
                "<span class='seat-tier-legend tier-silver'>Silver - 250</span>"
                "<span class='seat-tier-legend tier-regular'>Regular - 180</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div class='seat-grid'>", unsafe_allow_html=True)
            for row in ROWS:
                row_cols = st.columns([0.6] + [1] * SEATS_PER_ROW)
                with row_cols[0]:
                    st.markdown(f"<div class='seat-row-label'>{row}</div>", unsafe_allow_html=True)
                for i in range(SEATS_PER_ROW):
                    seat = f"{row}{i+1}"
                    with row_cols[i + 1]:
                        key = f"seat_{seat}_{show_key}"
                        checked = st.checkbox(
                            seat,
                            key=key,
                            disabled=seat in booked or st.session_state.booking_step == "payment",
                        )
                        st.markdown("<span class='tooltip-seat'></span>", unsafe_allow_html=True)
                    if checked:
                        selected_seats.append(seat)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
            total_seats = len(ROWS) * SEATS_PER_ROW
            booked_count = len(booked)
            selected_count = len(selected_seats)
            available_count = total_seats - booked_count - selected_count
            st.caption(
                f"Available: {available_count} | Selected: {selected_count} | Booked: {booked_count}"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
            st.markdown("<div class='booking-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Proceed to Payment</div>", unsafe_allow_html=True)
            if st.session_state.booking_step == "payment":
                st.info("Complete payment to confirm your ticket.")
                st.markdown("[Go to Payment Section](#payment-section)")
                proceed_clicked = False
            else:
                confirm_ok = st.checkbox("I confirm my selected seats and showtime")
                proceed_clicked = st.button(
                    "Book Tickets", key="proceed_payment_btn", disabled=not confirm_ok,
                    type="primary", icon=":material/local_activity:", use_container_width=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    
        if proceed_clicked:
            if len(selected_seats) == 0:
                st.warning("Please select seats")
            else:
                lock_map = get_lock_map(movie_choice, city, theatre, show_time, str(show_date))
                locked_by_others = {
                    seat for seat, user in lock_map.items() if user != st.session_state.username
                }
                if locked_by_others.intersection(set(selected_seats)):
                    st.error("Some selected seats were just locked by another user. Please reselect.")
                else:
                    lock_seats(
                        movie_choice,
                        city,
                        theatre,
                        show_time,
                        str(show_date),
                        selected_seats,
                        st.session_state.username,
                    )
                    st.session_state.pending_booking = {
                        "movie": movie_choice,
                        "city": city,
                        "theatre": theatre,
                        "show_time": show_time,
                        "show_date": str(show_date),
                        "seats": selected_seats,
                    }
                    st.session_state.booking_step = "payment"
                    st.success("Seats locked. Proceed to payment.")
                    st.session_state.scroll_to_payment = True
    
    with right:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Booking Summary</div>", unsafe_allow_html=True)
        summary_seats = []
        if st.session_state.booking_step == "payment" and st.session_state.pending_booking:
            summary_seats = st.session_state.pending_booking["seats"]
        elif now_titles:
            summary_seats = [s for s in selected_seats]
        seat_price_total = 0
        for s in summary_seats:
            row = s[0]
            seat_price_total += TIER_MAP.get(row, ("Regular", 180))[1]
        convenience_fee = 30
        gst = round(0.18 * (seat_price_total + convenience_fee), 2)
        total_price = round(seat_price_total + convenience_fee + gst, 2)
    
        st.write("Movie:", movie_choice)
        st.write("City:", city)
        st.write("Theatre:", theatre)
        st.write("Date:", str(show_date))
        st.write("Show Time:", show_time)
        st.write("Selected Seats:", ", ".join(summary_seats) if summary_seats else "None")
        st.markdown("</div>", unsafe_allow_html=True)
    
        if st.session_state.last_booking:
            lb = st.session_state.last_booking
            st.markdown("<div class='ticket-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Ticket Confirmation</div>", unsafe_allow_html=True)
            st.write("Booking ID:", lb["booking_id"])
            st.write("Movie:", lb["movie"])
            st.write("Theatre:", lb["theatre"])
            st.write("Location:", lb["city"])
            st.write("Date:", lb["show_date"])
            st.write("Time:", lb["show_time"])
            st.write("Seats:", ", ".join(lb["seats"]))
            st.write("Total Amount Paid:", lb["price"])
            ticket_text = (
                f"Booking ID: {lb['booking_id']}\n"
                f"Movie: {lb['movie']}\n"
                f"Theatre: {lb['theatre']}\n"
                f"Location: {lb['city']}\n"
                f"Date: {lb['show_date']}\n"
                f"Time: {lb['show_time']}\n"
                f"Seats: {', '.join(lb['seats'])}\n"
                f"Total: {lb['price']}\n"
            )
            try:
                import qrcode

                qr = qrcode.make(ticket_text)
                buf = BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf.getvalue(), width=140)
            except Exception:
                pass
            st.download_button(
                "Download Ticket",
                data=ticket_text,
                file_name=f"{lb['booking_id']}.txt",
                mime="text/plain",
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.booking_step == "payment" and st.session_state.pending_booking:
        pb = st.session_state.pending_booking
        seat_price_total = 0
        for s in pb["seats"]:
            row = s[0]
            seat_price_total += TIER_MAP.get(row, ("Regular", 180))[1]
        convenience_fee = 30
        gst = round(0.18 * (seat_price_total + convenience_fee), 2)
        total_price = round(seat_price_total + convenience_fee + gst, 2)
    
        if st.session_state.get("scroll_to_payment"):
            st.markdown("<a id='payment-section'></a>", unsafe_allow_html=True)
            st.session_state.scroll_to_payment = False
    
        st.markdown("<div class='payment-card'>", unsafe_allow_html=True)
        st.markdown("### Payment Summary")
        st.write("Movie:", pb["movie"])
        st.write("Theatre:", pb["theatre"])
        st.write("Location:", pb["city"])
        st.write("Date:", pb["show_date"])
        st.write("Show Time:", pb["show_time"])
        st.write("Seats:", ", ".join(pb["seats"]))
        st.write(f"Ticket Price (₹{seat_price_total} for {len(pb['seats'])} seats)")
        st.write("Convenience Fee:", convenience_fee)
        st.write("GST (18%):", gst)
        st.markdown(f"**Total Amount: ₹{total_price}**")
    
        st.markdown("### Payment Methods")
        payment_method = st.radio(
            "Select Payment Method",
            ["Card", "UPI", "Net Banking", "Wallet"],
            horizontal=True,
        )
        name_on_card = card_number = expiry = cvv = email = ""
        upi_id = ""
        bank_name = ""
        wallet_type = ""
    
        if payment_method == "Card":
            name_on_card = st.text_input("Name on Card")
            card_number = st.text_input("Card Number")
            expiry = st.text_input("Expiry (MM/YY)")
            cvv = st.text_input("CVV", type="password")
            email = st.text_input("Email")
        elif payment_method == "UPI":
            upi_id = st.text_input("UPI ID")
        elif payment_method == "Net Banking":
            bank_name = st.selectbox("Bank", ["", "HDFC", "ICICI", "SBI", "Axis"])
        elif payment_method == "Wallet":
            wallet_type = st.selectbox("Wallet", ["", "Paytm", "PhonePe", "Amazon Pay"])
    
        valid = False
        if payment_method == "Card":
            valid = bool(name_on_card and email and card_number and expiry and cvv)
        elif payment_method == "UPI":
            valid = bool(upi_id)
        elif payment_method == "Net Banking":
            valid = bool(bank_name)
        elif payment_method == "Wallet":
            valid = bool(wallet_type)
    
        pay_cols = st.columns([2, 1])
        with pay_cols[0]:
            pay = st.button(
                "Pay Now", key="pay_now_btn", disabled=not valid,
                type="primary", icon=":material/lock:", use_container_width=True,
            )
        with pay_cols[1]:
            cancel = st.button(
                "Cancel", key="cancel_payment_btn",
                type="secondary", use_container_width=True,
            )
        if cancel:
            release_seats(
                pb["movie"],
                pb["city"],
                pb["theatre"],
                pb["show_time"],
                pb["show_date"],
                pb["seats"],
                st.session_state.username,
            )
            st.session_state.pending_booking = None
            st.session_state.booking_step = "select"
            st.warning("Payment cancelled. Seats released.")
        if pay:
            ok = True
            if payment_method == "Card":
                if not (name_on_card and email and card_number and expiry and cvv):
                    st.error("Please fill all card details.")
                    ok = False
                elif "@" not in email:
                    st.error("Invalid email.")
                    ok = False
                elif len(card_number) != 16 or not card_number.isdigit():
                    st.error("Invalid card number.")
                    ok = False
                elif len(cvv) != 3 or not cvv.isdigit():
                    st.error("Invalid CVV.")
                    ok = False
            elif payment_method == "UPI":
                if not upi_id:
                    st.error("Enter UPI ID.")
                    ok = False
                elif "@" not in upi_id:
                    st.error("Invalid UPI ID.")
                    ok = False
            elif payment_method == "Net Banking":
                if not bank_name:
                    st.error("Select a bank.")
                    ok = False
            elif payment_method == "Wallet":
                if not wallet_type:
                    st.error("Select a wallet.")
                    ok = False
    
            if ok:
                booking_id = build_booking_id()
                c.execute(
                    "INSERT INTO bookings (username, movie, booking_id, city, theatre, show_time, show_date, seats, total_amount) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        st.session_state.username,
                        pb["movie"],
                        booking_id,
                        pb["city"],
                        pb["theatre"],
                        pb["show_time"],
                        pb["show_date"],
                        ",".join(pb["seats"]),
                        total_price,
                    ),
                )
                conn.commit()
                release_seats(
                    pb["movie"],
                    pb["city"],
                    pb["theatre"],
                    pb["show_time"],
                    pb["show_date"],
                    pb["seats"],
                    st.session_state.username,
                )
                st.session_state.last_booking = {
                    "booking_id": booking_id,
                    "movie": pb["movie"],
                    "city": pb["city"],
                    "theatre": pb["theatre"],
                    "show_time": pb["show_time"],
                    "show_date": pb["show_date"],
                    "seats": pb["seats"],
                    "price": total_price,
                }
                st.session_state.pending_booking = None
                st.session_state.booking_step = "select"
                st.success("Payment successful. Ticket confirmed.")
    
                c.execute("SELECT email FROM users WHERE username=?", (st.session_state.username,))
                row = c.fetchone()
                email = row[0] if row else None
                sent, msg = send_booking_email(
                    email,
                    {
                        "booking_id": booking_id,
                        "movie": pb["movie"],
                        "city": pb["city"],
                        "theatre": pb["theatre"],
                        "show_date": pb["show_date"],
                        "show_time": pb["show_time"],
                        "seats": pb["seats"],
                        "price": total_price,
                    },
                )
                if sent:
                    st.info("Ticket email sent.")
                else:
                    st.warning(f"Ticket email not sent: {msg}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Booking history and cancel booking removed from booking page
    
    

