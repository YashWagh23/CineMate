import streamlit as st
from utils import *

load_css()


def auth_page():
    def set_background():
        img_base64 = ""
        if os.path.exists("background.jpg"):
            with open("background.jpg", "rb") as img:
                img_base64 = b64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            html, body, .stApp {{
                height: 100%;
                margin: 0;
                padding: 0;
            }}
            .stApp {{
                background:
                    linear-gradient(180deg, rgba(10,10,13,0.55) 0%, rgba(10,10,13,0.82) 65%, rgba(10,10,13,0.96) 100%),
                    url("data:image/jpg;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            .block-container {{
                padding-top: 2.5rem !important;
                padding-bottom: 2.5rem !important;
            }}
            .main > div {{
                min-height: 100vh;
            }}
            .login-box .stButton > button {{
                width: 100%;
            }}
            .login-box [data-testid="stForm"] {{
                background: transparent;
                border: none;
                padding: 0 !important;
            }}
            header {{visibility: hidden;}}
            [data-testid="stToolbar"] {{display: none;}}
            [data-testid="stDecoration"] {{display: none;}}
            section[data-testid="stSidebar"] {{
                display: none !important;
                width: 0 !important;
            }}
            [data-testid="stSidebarNav"] {{display: none !important;}}
            [data-testid="stHeader"] {{display: none !important;}}
            </style>
            """,
            unsafe_allow_html=True,
        )

    set_background()

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "signup"

    left_col, mid_col, right_col = st.columns([1, 1.3, 1])
    with mid_col:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        with st.container(border=True):
            logo_path = os.path.join("assets", "logo.png")
            logo_cols = st.columns([1, 2, 1])
            with logo_cols[1]:
                if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
                    st.image(logo_path, use_container_width=True)
                else:
                    st.markdown(
                        "<div class='brand-word' style='text-align:center'>CINE<span class='accent'>MATE</span></div>",
                        unsafe_allow_html=True,
                    )
            st.markdown(
                "<div style='text-align:center;color:var(--muted);font-size:var(--fs-sm);"
                "margin:-4px 0 20px 0;'>Movies. Tickets. Recommendations.</div>",
                unsafe_allow_html=True,
            )

            if st.session_state.auth_mode == "login":
                st.markdown(
                    "<div class='brand-word' style='font-size:var(--fs-xl);margin-bottom:4px'>Welcome back</div>",
                    unsafe_allow_html=True,
                )
                st.caption("Log in to keep booking and tracking your watchlist.")

                u = st.text_input(
                    "Email or Username",
                    key="login_u",
                    value=st.session_state.remembered_user or "",
                    placeholder="you@example.com",
                )
                p = st.text_input("Password", type="password", key="login_p", placeholder="Your password")
                remember = st.checkbox("Remember me on this device", key="remember_me")

                if st.button("Log in", key="login_btn", type="primary", icon=":material/login:"):
                    user = login_user(u, p)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user[0]
                        st.session_state.role = user[5] if user[5] else "user"
                        st.session_state.remembered_user = u if remember else None
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

                st.markdown(
                    "<div style='text-align:center;color:var(--muted);font-size:var(--fs-sm);margin-top:16px'>"
                    "New to CineMate?</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Create an account", key="switch_signup", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
            else:
                st.markdown(
                    "<div class='brand-word' style='font-size:var(--fs-xl);margin-bottom:4px'>Join CineMate</div>",
                    unsafe_allow_html=True,
                )
                st.caption("Create an account to book tickets and save your favorites.")

                name_cols = st.columns(2)
                with name_cols[0]:
                    first_name = st.text_input("First Name", key="reg_first_name", placeholder="Jordan")
                with name_cols[1]:
                    last_name = st.text_input("Last Name", key="reg_last_name", placeholder="Rivera")

                ne = st.text_input("Email", key="reg_email", placeholder="you@example.com")
                np = st.text_input("Password", type="password", key="reg_password", placeholder="8+ chars, mixed case, number, symbol")

                if st.button("Create account", key="register_btn", type="primary", icon=":material/person_add:"):
                    nu = f"{first_name.strip()} {last_name.strip()}".strip() or "user"
                    ok, msg = register_user(nu, ne, np)
                    if ok:
                        st.success(msg)
                    else:
                        st.warning(msg)

                st.markdown(
                    "<div style='text-align:center;color:var(--muted);font-size:var(--fs-sm);margin-top:16px'>"
                    "Already have an account?</div>",
                    unsafe_allow_html=True,
                )
                if st.button("Log in instead", key="switch_login", type="secondary", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def ensure_role_loaded():
    if st.session_state.logged_in and st.session_state.username:
        c.execute("SELECT role FROM users WHERE username=?", (st.session_state.username,))
        row = c.fetchone()
        if row and row[0]:
            st.session_state.role = row[0]
