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
 
 
# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 TechCorp Support 00")
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("• OpenAI GPT-4o")
    st.markdown("• Pinecone Vector DB")
    st.markdown("• Multi-Agent System")
    st.markdown("---")
    st.markdown("**Agents:**")
    st.markdown("• 🎯 Triage Agent")
    st.markdown("• 🔬 Research Agent")
    st.markdown("• 🧭 Orchestrator")
    st.markdown("• 🗣️ Clarify Agent")
    st.markdown("---")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()
 
 
# ── Session ID ──────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = "default"
 
 
# ── Main chat interface ──────────────────────────────────
st.title("TechCorp Customer Support")
st.caption("Powered by multi-agent AI — ask me anything about your account")
 
# Initialize message history in session state
# session_state persists within the same browser tab
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Display all previous messages in chat bubbles
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
 
# ── Chat input ───────────────────────────────────────────
# := is walrus operator — assigns and checks in one line
# Only runs the block if user typed something
if prompt := st.chat_input("Type your support question..."):
 
    # Show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
 
    # Show agent response
    with st.chat_message("assistant"):
 
        # Spinner shows while orchestrator is running
        with st.spinner("Agent is thinking..."):
            response = orchestrate(
                prompt,
                session_id=st.session_state.session_id
            )
 
        # TRIAGE route returns dict — extract string
        # RESEARCH, OUT_OF_SCOPE, CLARIFY return strings directly
        if isinstance(response, dict):
            response = response["final_answer"]
 
        st.markdown(response)
 
    # Save to session history for display on next rerun
    st.session_state.messages.append({
        "role":    "assistant",
        "content": response
    })
