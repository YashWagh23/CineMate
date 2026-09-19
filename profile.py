import html
import streamlit as st
from utils import *

load_css()


def render_profile():
    st.markdown("<div class='section-title'>Profile</div>", unsafe_allow_html=True)
    if st.button("Logout", key="profile_logout_btn", type="secondary", icon=":material/logout:"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    c.execute(
        "SELECT username, email, role, created_at, profile_image FROM users WHERE username=?",
        (st.session_state.username,),
    )
    user_row = c.fetchone()
    username = user_row[0] if user_row else st.session_state.username
    email_val = user_row[1] if user_row else None
    role_val = user_row[2] if user_row else "user"
    created_val = user_row[3] if user_row else None
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        profile_img = get_profile_image(username)
        if profile_img:
            st.image(profile_img, width=120)
        else:
            initials = html.escape((username or "U")[:2].upper())
            st.markdown(f"<div class='avatar-circle'>{initials}</div>", unsafe_allow_html=True)
    
        uploaded_file = st.file_uploader(
            "Upload Profile Picture", type=["jpg", "png"], key="profile_upload"
        )
        if uploaded_file and st.button("Save Photo", key="save_profile_photo", type="primary", icon=":material/upload:"):
            saved_path = save_profile_image(username, uploaded_file)
            if saved_path:
                c.execute(
                    "UPDATE users SET profile_image=? WHERE username=?",
                    (saved_path, username),
                )
                conn.commit()
                st.success("Profile photo updated successfully")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Profile Info</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='profile-label'>Username</div><div class='profile-value'>{html.escape(username or '')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='profile-label'>Email</div><div class='profile-value'>{html.escape(email_val) if email_val else 'Not set'}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='profile-label'>Role</div><div class='profile-value'>{html.escape(role_val or 'user')}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='profile-label'>Member since</div><div class='profile-value'>{html.escape(created_val) if created_val else 'Unknown'}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Edit Profile</div>", unsafe_allow_html=True)
    with st.form("edit_profile_form"):
        new_email = st.text_input("Update Email", value=email_val or "")
        submitted = st.form_submit_button("Save Changes", type="primary", icon=":material/save:")
    if submitted:
        updates = []
        params = []
        if new_email and new_email != (email_val or ""):
            if not is_valid_email(new_email):
                st.error("Enter a valid email address")
            else:
                c.execute("SELECT 1 FROM users WHERE email=?", (new_email,))
                if c.fetchone():
                    st.error("Email already exists")
                else:
                    updates.append("email=?")
                    params.append(new_email)
        if updates:
            params.append(username)
            c.execute(
                "UPDATE users SET " + ", ".join(updates) + " WHERE username=?",
                params,
            )
            conn.commit()
            st.success("Profile updated successfully")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Change Password</div>", unsafe_allow_html=True)
    with st.form("change_password_form"):
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        pw_submit = st.form_submit_button("Update Password", type="primary", icon=":material/key:")
    if pw_submit:
        c.execute(
            "SELECT password_hash, salt, password FROM users WHERE username=?",
            (username,),
        )
        row = c.fetchone()
        stored_hash, stored_salt, legacy_pw = row if row else (None, None, None)
        current_ok = False
        if stored_hash and stored_salt:
            check_hash, _ = hash_password(current_pw, salt_b64=stored_salt)
            current_ok = check_hash == stored_hash
        elif legacy_pw:
            current_ok = legacy_pw == current_pw
    
        if not current_ok:
            st.error("Incorrect current password")
        else:
            issues = password_issues(new_pw)
            if issues:
                st.error("Password must have " + ", ".join(issues))
            elif new_pw != confirm_pw:
                st.error("New password and confirm password do not match")
            else:
                pw_hash, salt = hash_password(new_pw)
                c.execute(
                    "UPDATE users SET password_hash=?, salt=?, password=NULL WHERE username=?",
                    (pw_hash, salt, username),
                )
                conn.commit()
                st.success("Password changed successfully")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your Booking History</div>", unsafe_allow_html=True)
    c.execute("PRAGMA table_info(bookings)")
    available_cols = [row[1] for row in c.fetchall()]
    desired_cols = [
        "booking_id",
        "movie",
        "city",
        "theatre",
        "show_time",
        "show_date",
        "seats",
    ]
    cols_to_select = [col for col in desired_cols if col in available_cols]
    if not cols_to_select:
        cols_to_select = ["movie"]
    select_sql = (
        "SELECT " + ", ".join(cols_to_select) + " FROM bookings WHERE username=?"
    )
    user_bookings = pd.read_sql_query(
        select_sql,
        conn,
        params=(st.session_state.username,),
    )
    for col in desired_cols:
        if col not in user_bookings.columns:
            user_bookings[col] = None
    user_bookings = user_bookings[desired_cols]
    if user_bookings.empty:
        st.info("No bookings yet.")
    else:
        for _, row in user_bookings.iterrows():
            movie = row.get("movie") or "Unknown"
            city = row.get("city") or "N/A"
            theatre = row.get("theatre") or "N/A"
            show_time = row.get("show_time") or "N/A"
            show_date = row.get("show_date") or "N/A"
            seats = row.get("seats") or "N/A"
            booking_id = row.get("booking_id") or "N/A"
            st.markdown(
                f"""
                <div class="booking-history-card">
                    <div>
                        <div class="bh-title">🎬 {movie}</div>
                        <div class="bh-sub">📍 {city} | {theatre}</div>
                        <div class="bh-sub">🕒 {show_time} • {show_date}</div>
                    </div>
                    <div>
                        <div class="bh-seat">🎟 {seats}</div>
                        <div class="bh-id">🆔 {booking_id}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
    
    

