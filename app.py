# app.py — Dark immersive theme
import streamlit as st
import os, sys, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from agents.orchestrator import orchestrate

st.set_page_config(
    page_title="TechCorp Support",
    page_icon="🤖",
    layout="wide"
)

# ── Dark theme CSS ────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f172a;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }

    /* All text in sidebar */
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Chat message background — user */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #1e293b;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Chat message background — assistant */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #1e293b;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* All text color */
    .stMarkdown, p, span, div {
        color: #e2e8f0;
    }

    /* Chat input box */
    [data-testid="stChatInput"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 24px !important;
        color: #e2e8f0 !important;
    }

    /* Chat input text */
    [data-testid="stChatInput"] textarea {
        color: #e2e8f0 !important;
        background-color: transparent !important;
    }

    /* Title */
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }

    /* Caption */
    .stCaption {
        color: #64748b !important;
    }

    /* Button */
    .stButton button {
        background-color: #334155;
        color: #e2e8f0;
        border: 1px solid #475569;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #475569;
        border-color: #64748b;
    }

    /* Spinner */
    .stSpinner {
        color: #3b82f6 !important;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main content padding */
    .block-container {
        padding-top: 2rem;
        max-width: 860px;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 TechCorp Support")
    st.markdown("---")

    # Online status indicator
    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
        <div style="width:8px; height:8px; border-radius:50%; background:#22c55e;"></div>
        <span style="font-size:13px; color:#94a3b8;">Online — all agents ready</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Agents**")
    st.markdown("🎯 Triage Agent")
    st.markdown("🔬 Research Agent")
    st.markdown("🧭 Orchestrator")
    st.markdown("🗣️ Clarify Agent")
    st.markdown("---")
    st.markdown("**Powered by**")
    st.markdown("• OpenAI GPT-4o")
    st.markdown("• Pinecone Vector DB")
    st.markdown("• Supabase PostgreSQL")
    st.markdown("---")

    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()


# ── Session ID ────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "default"


# ── Header ────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
    <div style="width:36px; height:36px; border-radius:50%; background:#3b82f6;
                display:flex; align-items:center; justify-content:center;
                font-size:16px;">🤖</div>
    <div>
        <h1 style="font-size:22px; margin:0; color:#f1f5f9;">TechCorp Customer Support</h1>
    </div>
</div>
""", unsafe_allow_html=True)
st.caption("Multi-agent AI — ask me anything about your account, billing, or technical issues")
st.markdown("---")


# ── Message history ───────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ── Chat input ────────────────────────────────────────────
if prompt := st.chat_input("Type your support question..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("▌")

        import time
        response = orchestrate(
            prompt,
            session_id=st.session_state.session_id
        )

        if isinstance(response, dict):
            response = response["final_answer"]

        # Character by character streaming effect
        full_response = ""
        for char in response:
            full_response += char
            placeholder.markdown(full_response + "▌")
            time.sleep(0.008)

        placeholder.markdown(full_response)
        response = full_response

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response
    })
