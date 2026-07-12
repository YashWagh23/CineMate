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
                background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)),
                            url("data:image/jpg;base64,{img_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            .block-container {{
                padding-top: 0rem !important;
                padding-bottom: 0rem !important;
            }}
            .main > div {{
                height: 100vh;
            }}
            .login-box {{
                width: 380px;
                max-width: 90vw;
                padding: 30px;
                border-radius: 15px;
                background: rgba(0,0,0,0.6);
                backdrop-filter: blur(12px);
                text-align: left;
                box-shadow: 0 18px 40px rgba(0,0,0,0.45);
                margin: 0 auto;
            }}
            .login-box img {{
                display: block;
                margin: 0 auto 12px auto;
            }}
            .login-box .subtle {{
                color: #e5e7eb;
                font-size: 0.9rem;
                text-align: center;
                margin-top: 8px;
                margin-bottom: 6px;
            }}
            .login-box .title {{
                text-align: center;
                font-size: 1.5rem;
                font-weight: 800;
                margin-top: 6px;
            }}
            .login-box div[data-baseweb="input"] {{
                width: 100% !important;
                max-width: 100% !important;
                margin: 0 auto 15px auto;
                border-radius: 10px;
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.18);
            }}
            .login-box input {{
                border-radius: 10px !important;
                color: #ffffff !important;
            }}
            .login-box .stButton > button {{
                width: 100%;
                border-radius: 20px;
                background: #ff2c2c;
                font-weight: 700;
                transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
            }}
            .login-box .stButton > button:hover {{
                background: #e11f1f;
                transform: translateY(-1px) scale(1.02);
                box-shadow: 0 8px 18px rgba(255,44,44,0.35);
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

    left_col, mid_col, right_col = st.columns([1, 2, 1])
    with mid_col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)

        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
            st.image(logo_path, width=130)
        else:
            st.markdown("### Cinemate")

        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "signup"

        if st.session_state.auth_mode == "login":
            st.markdown("<div class='subtle'>New here? Sign Up</div>", unsafe_allow_html=True)
            if st.button("Switch to Sign Up", key="switch_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()
            st.markdown("<div class='title'>Login</div>", unsafe_allow_html=True)

            u = st.text_input(
                "Email or Username",
                key="login_u",
                value=st.session_state.remembered_user or "",
            )
            p = st.text_input("Password", type="password", key="login_p")
            remember = st.checkbox("Remember me on this device", key="remember_me")

            if st.button("Login", key="login_btn"):
                user = login_user(u, p)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.role = user[5] if user[5] else "user"
                    st.session_state.remembered_user = u if remember else None
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            st.markdown("<div class='subtle'>Have an account? Login</div>", unsafe_allow_html=True)
            if st.button("Switch to Login", key="switch_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
            st.markdown("<div class='title'>Sign Up</div>", unsafe_allow_html=True)

            name_cols = st.columns(2)
            with name_cols[0]:
                first_name = st.text_input("First Name", key="reg_first_name")
            with name_cols[1]:
                last_name = st.text_input("Last Name", key="reg_last_name")

            ne = st.text_input("Email", key="reg_email")
            np = st.text_input("Password", type="password", key="reg_password")

            if st.button("Register", key="register_btn"):
                nu = f"{first_name.strip()} {last_name.strip()}".strip() or "user"
                ok, msg = register_user(nu, ne, np)
                if ok:
                    st.success(msg)
                else:
                    st.warning(msg)

        st.markdown("</div>", unsafe_allow_html=True)


def ensure_role_loaded():
    if st.session_state.logged_in and st.session_state.username:
        c.execute("SELECT role FROM users WHERE username=?", (st.session_state.username,))
        row = c.fetchone()
        if row and row[0]:
            st.session_state.role = row[0]
