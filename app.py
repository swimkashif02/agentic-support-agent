# ─────────────────────────────────────────────────────────
# Streamlit chat interface for the multi-agent support system.
# Run locally: streamlit run app.py
# Deploy: share.streamlit.io
# ─────────────────────────────────────────────────────────
 
import streamlit as st
import os, sys
 
# Ensure Python finds all project modules from root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
 
from agents.orchestrator import orchestrate
 
 
# ── Page configuration ───────────────────────────────────
# Must be the first Streamlit call in the script
st.set_page_config(
    page_title="TechCorp Support Agent",
    page_icon="🤖",
    layout="wide"
)
 
# ── Global CSS ────────────────────────────────────────────
st.markdown("""
<style>
    div[data-testid="stPills"] button[aria-selected="true"] {
        background-color: #dbeafe !important;
        color: #1e40af !important;
        border-color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 TechCorp")
    st.markdown("<div style='margin:8px 0; border-top:1px solid #e5e7eb;'></div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:13px; line-height:2;">
        <div style="font-weight:600; color:#374151; margin-bottom:2px;">Powered by</div>
        <div style="color:#6b7280;">OpenAI GPT-4o</div>
        <div style="color:#6b7280;">Pinecone Vector DB</div>
        <div style="color:#6b7280;">Multi-Agent System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:8px 0; border-top:1px solid #e5e7eb;'></div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:13px; line-height:2;">
        <div style="font-weight:600; color:#374151; margin-bottom:2px;">Agents</div>
        <div style="color:#6b7280;">🎯 Triage Agent</div>
        <div style="color:#6b7280;">🔬 Research Agent</div>
        <div style="color:#6b7280;">🧭 Orchestrator</div>
        <div style="color:#6b7280;">🗣️ Clarify Agent</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin:8px 0; border-top:1px solid #e5e7eb;'></div>",
                unsafe_allow_html=True)

    # ── Feedback form — pinned to bottom ──────────────────
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin:8px 0; border-top:1px solid #e5e7eb;'></div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:12px; font-weight:600; color:#374151; margin-bottom:6px;">
        💬 Leave feedback
    </div>
    """, unsafe_allow_html=True)

    from data.database import save_feedback

    with st.form("feedback_form", clear_on_submit=True):
        email    = st.text_input("Email", placeholder="your@email.com",
                                 label_visibility="collapsed")
        feedback = st.text_area("Feedback", placeholder="Tell us what you think...",
                                height=80, label_visibility="collapsed")
        submitted = st.form_submit_button("Send feedback", use_container_width=True)

        if submitted:
            if email.strip() and feedback.strip():
                success = save_feedback(email.strip(), feedback.strip())
                if success:
                    st.success("Thank you!")
                else:
                    st.error("Failed. Please try again.")
            else:
                st.warning("Please fill in both fields.")
 
# ── Session ID ──────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "default"
 
 
# ── Title row with Restart button ────────────────────────
title_row = st.container()

with title_row:
    col1, col2 = st.columns([8, 1], vertical_alignment="bottom")

    with col1:
        st.title("TechCorp Customer Support")

    with col2:
        has_messages = bool(st.session_state.get("messages"))
        has_selection = bool(st.session_state.get("selected_suggestion"))

        if has_messages or has_selection:
            if st.button("🔄 Clear Conversation", use_container_width=True):
                st.session_state.messages = []
                if "selected_suggestion" in st.session_state:
                    del st.session_state["selected_suggestion"]
                st.rerun()
st.markdown("""
<div style="background:#eff6ff; border-left:4px solid #3b82f6; border-radius:8px;
            padding:14px 18px; margin-bottom:20px; line-height:1.8;">
    <div style="font-size:15px; color:#1e40af;">
        Multi-agent AI system for customer support automation,
        featuring a 5-route orchestrator, RAG pipeline with Pinecone semantic search,
        persistent memory, and an evaluation framework.
        &nbsp;·&nbsp;
        <a href="https://github.com/swimkashif02/agentic-support-agent"
           style="color:#2563eb; text-decoration:none; font-weight:500;">GitHub ↗</a>
    </div>
    <div style="font-size:18px; color:#1e40af; margin-top:20px;">
        This is a demo project created by <strong>Kashif Riaz</strong>
    </div>
</div>
""", unsafe_allow_html=True)

 
# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous messages in chat bubbles
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ── Chat input ───────────────────────────────────────────
chat_input = st.chat_input("Type your support question...")

# ── Suggested questions — below chat input, empty chat only ──
SUGGESTIONS = [
    "My app crashes every time I try to log in",
    "I was charged twice this month",
    "Check my ticket TKT-12345",
    "Give me a report of all escalations",
]

if not st.session_state.messages:
    selected = st.pills(
        label="Try asking:",
        options=SUGGESTIONS,
        key="selected_suggestion",
        selection_mode="single"
    )
else:
    selected = None

# Resolve prompt — chat input takes priority over pill selection
if chat_input:
    prompt = chat_input
elif selected:
    prompt = selected
else:
    prompt = None

if prompt:

    # Clear pills and save prompt — rerun immediately so pills disappear
    if "selected_suggestion" in st.session_state:
        del st.session_state["selected_suggestion"]

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state["pending_prompt"] = prompt
    st.rerun()


# ── Process pending prompt after rerun ────────────────────
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            response = orchestrate(
                prompt,
                session_id=st.session_state.session_id
            )

        if isinstance(response, dict):
            response = response["final_answer"]

        # Show response immediately — no fake animation
        st.markdown(response)

    st.session_state.messages.append({
        "role":    "assistant",
        "content": response
    })