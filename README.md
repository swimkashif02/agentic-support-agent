# Agentic Customer Support System

A production-ready multi-agent AI system built with Python and OpenAI GPT-4o.
Demonstrates core agentic AI patterns including tool use, prompt engineering,
and function calling.

## Architecture
- Triage Agent — Classifies tickets and retrieves FAQ answers via tool use
- Tool Layer — search_faq, get_ticket_status, create_escalation
- FAQ Knowledge Base — 20 entries across BILLING, TECHNICAL, and ACCOUNT

## Tech Stack
- Python 3.11
- OpenAI GPT-4o API
- python-dotenv (environment management)

## What is built

### Week 1 — Complete
- LLM API integration with OpenAI GPT-4o
- Prompt engineering — system prompt, chain of thought, guardrails
- Tool definitions — search_faq, get_ticket_status, create_escalation
- Complete agentic loop with tool calling
- FAQ knowledge base with 20 entries
- All 4 test cases passing

### Week 2 — Complete
- OpenAI text-embedding-3-small embeddings (1536 dimensions)
- Pinecone vector database — 20 FAQs ingested as vectors
- Chunking strategy — question + answer combined per chunk
- Semantic retrieval — search by meaning not keywords
- Multi-stage retrieval — broad search (top 10) then rerank to top 3
- Query rewriting — rule-based optimisation before searching
- Score threshold 0.30 — tuned for text-embedding-3-small

## Setup

pip install -r requirements.txt

Add your OPENAI_API_KEY to the .env file:

OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx

## Running

Run the triage agent:
py -m agents.triage_agent

Run the main API demo:
py main.py

## Project Structure

agentic-support-agent/
├── agents/
│   └── triage_agent.py     ← Complete agentic loop
├── tools/
│   └── search_tool.py      ← Tool definitions + FAQ database
├── main.py                 ← API call demos (3 levels)
├── .env                    ← API keys (never commit)
└── requirements.txt