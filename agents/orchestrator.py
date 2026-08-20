import os, json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from agents.triage_agent import run_agent as run_triage
from data.database import save_message, load_history
from agents.research_agent import run_research
import asyncio

load_dotenv(find_dotenv(), override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ORCHESTRATOR_PROMPT = """You are the orchestrator agent for TechCorp support.

You receive user messages and decide which agent to delegate to.

TRIAGE AGENT — use when:
- Customer has a specific problem needing immediate solution
- Customer mentions a ticket number
- Customer asks how to do something specific
- Customer reports a bug, error, or issue
- Must be related to TechCorp software or services

RESEARCH AGENT — use when:
- User asks for a summary or report
- User asks about patterns or trends
- User asks "how many" or "what are common issues"
- User asks for analysis across multiple issues

BOTH AGENTS — use when message has two parts:
- Customer has a problem AND asks if it is common
- Customer wants help AND wants a report

OUT_OF_SCOPE — use ONLY when:
- Message is clearly personal — health, weather, food, relationships
- Message is completely unrelated to software, accounts, billing, or support
- Examples: "my stomach hurts", "what is the weather", "recommend a movie"

NEVER use OUT_OF_SCOPE for:
- Short or ambiguous messages that could be support related
- Follow-up messages that make sense in a support context

CLARIFY — use when:
- Message is too short or vague to determine intent
- Message could mean multiple completely different things
- You cannot confidently route to any of the above
- Examples: "generate all", "help", "yes", "ok", "do it"

IMPORTNAT - Do NOT use CLARIFY if:
- The conversation history already makes the intent clear
- The user is responding to a clarification question you already asked
- Combining this message with recent hisotry reveals a clear intent
- When in doubt and history exists - make your best inference and route

Respond ONLY with this JSON — no extra text:
{
  "route": "TRIAGE" | "RESEARCH" | "BOTH" | "OUT_OF_SCOPE" | "CLARIFY",
  "reasoning": "one sentence explaining your routing decision"
}"""

# ── Async wrappers for batching ──────────────────────────────
# These wrap the regular functions so asyncio can run them in parallel

async def run_triage_async(message: str) -> str:
    """Async wrapper for triage agent — runs in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_triage, message)


async def run_research_async(message: str) -> str:
    """Async wrapper for research agent — runs in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_research, message)


async def orchestrate_both(user_message: str) -> str:
    """Run both agents in parallel when route is BOTH."""
    print("  Running both agents in parallel...")

    # asyncio.gather runs both at the same time
    triage_result, research_result = await asyncio.gather(
        run_triage_async(user_message),
        run_research_async(user_message)
    )

    return f"{triage_result}\n\n---\n\n{research_result}"

def orchestrate(user_message: str, session_id: str = "default") -> str:
    """
    Main orchestrator function.
    Step 1: Decide which agent(s) to use
    Step 2: Call the right agent(s)
    Step 3: Combine results and return final response
    """

    print(f"\n{'='*55}")
    print(f"ORCHESTRATOR received: {user_message}")
    print(f"{'='*55}")

    # Save user message to history for all routes
    save_message(session_id, "user", user_message)

    # Load recent history to give routing context
    history = load_history(session_id, limit=4)

    # Step 1: Ask LLM which agent to route to — with history context
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=150,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_PROMPT},
            *history,                         
            {"role": "user",   "content": user_message}
        ]
    )

    raw = response.choices[0].message.content or ""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        routing = json.loads(raw)
    except:
        routing = {"route": "TRIAGE", "reasoning": "parse error fallback"}

    route = routing["route"]
    print(f"Routing decision: {route}")
    print(f"Reasoning: {routing['reasoning']}")

    if route == "TRIAGE":
        result = run_triage(user_message, session_id)
        if isinstance(result, dict):
            save_message(session_id, "assistant", result["final_answer"])
            result = result["final_answer"] 

    elif route == "RESEARCH":
        result = run_research(user_message)
        save_message(session_id, "assistant", result)

    elif route == "BOTH":
        result = asyncio.run(orchestrate_both(user_message))
        save_message(session_id, "assistant", result)

    elif route == "OUT_OF_SCOPE":
        result = "I am TechCorp support — I can only help with TechCorp software and services."
        save_message(session_id, "assistant", result)

    elif route == "CLARIFY":
        clarify_response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=150,
            messages=[
                {"role": "system", "content": """You are a TechCorp support agent.
    The user sent a vague message and you need to ask for clarification.

    TechCorp support system can help with:
    - Customer support tickets (open/closed ticket status and history)
    - Escalations (issues escalated to the support team)
    - Technical issues with the TechCorp app
    - Billing and account problems
    - FAQ answers about TechCorp products

    IMPORTANT: Check the conversation history above.
    If the user already answered a previous clarification — do NOT ask again.
    Instead confirm what you understood and proceed.

    Ask ONE short friendly question specific to what the user said.
    Keep it to 2-3 sentences maximum."""},
                *history,                    # ← inject history here too
                {"role": "user", "content": user_message}
            ]
        )
        result = clarify_response.choices[0].message.content
        save_message(session_id, "assistant", result)

    else:
        result = "Could not determine routing. Please try again."   

    return result

if __name__ == "__main__":
    while True:
        msg = input("\nYou: ").strip()
        if msg == "exit": break
        result = orchestrate(msg)
        print(f"\nFINAL ANSWER:\n{result}")
