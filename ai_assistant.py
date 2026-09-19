import html
import streamlit as st
from utils import *

load_css()


def render_ai_assistant():
    # tabs index: 0 Home, 1 Book Tickets, 2 AI Assistant, 3 Watchlist, 4 Profile
    st.markdown("<div class='section-title'>AI Movie Assistant</div>", unsafe_allow_html=True)
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    quick_message = None
    model_test = get_gemini_model()
    if model_test is None:
        st.info("Gemini is not configured. Install google-generativeai and set GEMINI_API_KEY in .env.")
    
    def handle_message(text):
        st.session_state.chat_messages.append({"role": "user", "content": text})
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            "<div class='msg-row ai'><div class='bubble ai'>Cinemate is typing...</div></div>",
            unsafe_allow_html=True,
        )
        time.sleep(1.2)
        typing_placeholder.empty()
        history = [
            f"{'User' if m.get('role') == 'user' else 'AI'}: {m.get('content')}"
            for m in st.session_state.chat_messages
        ]
        reply = get_ai_response(text, history)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
    
    st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_messages:
        role = msg.get("role")
        content = msg.get("content", "")
        row_class = "msg-row user" if role == "user" else "msg-row ai"
        bubble_class = "bubble user" if role == "user" else "bubble ai"
        safe_content = html.escape(content).replace("\n", "<br>")
        st.markdown(
            f"<div class='{row_class}'><div class='{bubble_class}'>{safe_content}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div id='chat-bottom'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Type a message...", key="chat_input")
        sent = st.form_submit_button("Send", type="primary", icon=":material/send:")
    if sent and user_msg:
        handle_message(user_msg)
        st.rerun()
    
    if st.button("Clear Conversation", key="chat_clear_btn", type="secondary", icon=":material/delete_sweep:"):
        st.session_state.chat_messages = []
        st.rerun()
    
    

