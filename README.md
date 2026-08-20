# Agentic Customer Support System
 
A production-ready multi-agent AI system for customer support automation.
Built with Python, OpenAI GPT-4o, Pinecone, and Streamlit.
 
Live demo: [LINK]
 
## Architecture
- Orchestrator Agent — 5-route routing: TRIAGE / RESEARCH / BOTH / OUT_OF_SCOPE / CLARIFY
- Triage Agent — FAQ search via RAG, ticket lookup, escalation, long-term memory
- Research Agent — ticket and escalation analysis, structured report generation
- Clarify Agent — dynamic context-aware clarification for ambiguous messages
- RAG Pipeline — Pinecone semantic search with query rewriting and reranking
- Database — SQLite (local) or Supabase PostgreSQL (cloud) via one-line toggle
- Cache — persistent Pinecone result cache to avoid repeat API calls
- Streamlit Frontend — live chat UI with per-session memory
 
## Tech Stack
- Python 3.11
- OpenAI GPT-4o API + text-embedding-3-small
- Pinecone (managed vector database)
- SQLite (local development) / Supabase PostgreSQL (cloud deployment)
- Streamlit (frontend + Streamlit Community Cloud hosting)
 
## Eval Results
- Test set: 20 real customer questions across BILLING, TECHNICAL, ACCOUNT
- Rule-based score: XX/20 (XX%)
- LLM-as-judge average: X.X/5
 
## Project Files
- main.py — terminal entry point (all 4 levels + multi-agent system)
- app.py — Streamlit chat UI
- agents/orchestrator.py — 5-route orchestrator with memory and CLARIFY
- agents/triage_agent.py — agentic loop with long-term memory
- agents/research_agent.py — analysis and report generation
- agents/clarify_agent.py — dynamic clarification agent
- rag/retriever.py — RAG pipeline with cache
- data/database.py — DB_BACKEND toggle (sqlite or supabase)
- evals/ — test set, graders, results
 
## Setup
# Install dependencies
pip install -r requirements.txt
 
# Create database (SQLite — local only)
python data/setup_db.py
 
# Ingest FAQs into Pinecone (run once)
py -m rag.ingest
 
# Run terminal version
python main.py
 
# Run Streamlit UI
streamlit run app.py

## Roadmap
- [x] Week 1 — Foundations + LLM API + Tool Use
- [x] Week 2 — RAG Pipeline + Pinecone Vector DB
- [x] Week 3 — Multi-Agent Architecture + Memory + Performance
- [x] Week 4 — Evals + Streamlit Frontend + Deployment