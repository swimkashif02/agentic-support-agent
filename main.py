import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ─────────────────────────────────────────────────────────────
# LEVEL 1: The most basic possible call
# ─────────────────────────────────────────────────────────────
def simple_llm_call(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
# LEVEL 2: With a system prompt (agent identity)
# ─────────────────────────────────────────────────────────────
def llm_with_system_prompt(system: str, user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
# LEVEL 3: With structured JSON output (parseable by code)
# ─────────────────────────────────────────────────────────────
def classify_ticket(user_message: str) -> dict:
    system = """You are a support triage classifier.
    Respond ONLY with this JSON — no other text, no markdown backticks:
    {
      "category": "BILLING" | "TECHNICAL" | "ACCOUNT",
      "confidence": 0.0 to 1.0,
      "action": "ANSWER" | "ESCALATE",
      "reason": "one sentence explanation"
    }"""
    raw = llm_with_system_prompt(system, user_message)
    return json.loads(raw)


# ─────────────────────────────────────────────────────────────
# LEVEL 4: All 6 prompt engineering techniques + user input
#
# Techniques used:
#   1. System Prompt      — agent identity and role
#   2. Few-Shot Examples  — 3 examples of correct classification
#   3. Chain of Thought   — step-by-step reasoning before answer
#   4. Output Format      — strict JSON structure
#   5. Guardrails         — rules the LLM must never break
#   6. Context Injection  — customer name and tier injected at runtime
# ─────────────────────────────────────────────────────────────
def full_prompt_engineering(user_message: str,
                             customer_name: str,
                             account_tier: str) -> dict:

    # ── Technique 1: System Prompt (agent identity) ──────────
    # ── Technique 2: Few-Shot Examples ───────────────────────
    # ── Technique 3: Chain of Thought ────────────────────────
    # ── Technique 4: Output Format Control ───────────────────
    # ── Technique 5: Guardrails ──────────────────────────────
    # ── Technique 6: Context Injection ───────────────────────
    system = f"""You are a customer support triage agent for TechCorp.
Your job is to classify incoming support messages and decide the best action.

---

EXAMPLES OF CORRECT CLASSIFICATION (Few-Shot):

Message: "My invoice shows a double charge this month"
Classification: BILLING | Confidence: 0.95 | Action: ANSWER
Response: "Duplicate charges are automatically reversed within 3-5 business days."

Message: "The app crashes every time I try to log in"
Classification: TECHNICAL | Confidence: 0.92 | Action: ANSWER
Response: "Please clear your app cache and update to the latest version."

Message: "I want to change my account email address"
Classification: ACCOUNT | Confidence: 0.97 | Action: ANSWER
Response: "Go to Settings > Profile > Email to update your address."

---

THINK STEP BY STEP before responding (Chain of Thought):
Step 1: What is the customer actually complaining about?
Step 2: Which category fits — BILLING, TECHNICAL, or ACCOUNT?
Step 3: How confident am I on a scale of 0.0 to 1.0?
Step 4: Can I answer directly or do I need to escalate?
Step 5: What is the ideal, personalized response for this customer?

---

RULES YOU MUST NEVER BREAK (Guardrails):
- Never invent policy information not shown in the examples above
- Never promise refunds or timelines you are not certain about
- If confidence is below 0.7, always set action to ESCALATE
- If the message is completely unclear, always set action to ESCALATE
- Always address the customer by their first name in the response

---

CUSTOMER CONTEXT (Context Injection):
Customer Name : {customer_name}
Account Tier  : {account_tier}
Current Date  : July 2026

Enterprise customers should receive priority handling and faster escalation.

---

OUTPUT FORMAT — respond ONLY with this JSON, no extra text:
{{
  "category"          : "BILLING" | "TECHNICAL" | "ACCOUNT",
  "confidence"        : 0.0 to 1.0,
  "action"            : "ANSWER" | "ESCALATE",
  "customer_response" : "personalized message addressing {customer_name} by name",
  "reasoning"         : "one sentence explaining your classification",
  "priority"          : "LOW" | "MEDIUM" | "HIGH"
}}"""

    raw = llm_with_system_prompt(system, user_message)
    return json.loads(raw)


# ─────────────────────────────────────────────────────────────
# OUTPUT HELPERS
# ─────────────────────────────────────────────────────────────
def print_header(level: str, title: str):
    print()
    print("=" * 60)
    print(f"  {level}: {title}")
    print("=" * 60)

def print_divider():
    print("-" * 60)

def print_input(text: str):
    print(f"  INPUT  : {text}")
    print_divider()

def print_output(text: str):
    print(f"  OUTPUT : {text}")

def print_menu():
    print()
    print("=" * 60)
    print("  AGENTIC AI COURSE — Week 1 Demo")
    print("=" * 60)
    print("  Select a function to run:")
    print()
    print("  1 — Basic call (no prompt engineering)")
    print("  2 — With system prompt (agent identity)")
    print("  3 — Structured JSON output (ticket classifier)")
    print("  4 — All 6 techniques combined (user input)")
    print("  5 — Run all levels automatically")
    print("  0 — Exit")
    print()


# ─────────────────────────────────────────────────────────────
# INDIVIDUAL RUNNERS
# ─────────────────────────────────────────────────────────────
def run_level_1():
    print_header("LEVEL 1", "Basic Call — No System Prompt")
    msg = input("  Enter your message: ").strip()
    if not msg:
        msg = "What does a support triage agent do?"
        print(f"  (using default: {msg})")
    print_input(msg)
    result = simple_llm_call(msg)
    print_output(result)


def run_level_2():
    print_header("LEVEL 2", "With System Prompt — Agent Identity")
    system = "You are a friendly support agent for TechCorp. Be concise."
    print(f"  SYSTEM : {system}")
    print_divider()
    msg = input("  Enter your message: ").strip()
    if not msg:
        msg = "How do I reset my password?"
        print(f"  (using default: {msg})")
    print_input(msg)
    result = llm_with_system_prompt(system, msg)
    print_output(result)


def run_level_3():
    print_header("LEVEL 3", "Structured JSON Output — Ticket Classifier")
    msg = input("  Enter your support ticket message: ").strip()
    if not msg:
        msg = "App crashes when I log in"
        print(f"  (using default: {msg})")
    print_input(msg)
    result = classify_ticket(msg)
    print(f"  Category   : {result['category']}")
    print(f"  Confidence : {result['confidence']}")
    print(f"  Action     : {result['action']}")
    print(f"  Reason     : {result['reason']}")


def run_level_4():
    print_header("LEVEL 4", "All 6 Techniques — Full Prompt Engineering")
    print()
    print("  This level uses all 6 prompt engineering techniques:")
    print("  System prompt, few-shot examples, chain of thought,")
    print("  output format, guardrails, and context injection.")
    print()
    print_divider()

    # Get user inputs
    customer_name = input("  Enter customer name       : ").strip()
    if not customer_name:
        customer_name = "Kashif"
        print(f"  (using default: {customer_name})")

    print("  Account tier options: FREE / PRO / ENTERPRISE")
    account_tier = input("  Enter account tier        : ").strip().upper()
    if account_tier not in ["FREE", "PRO", "ENTERPRISE"]:
        account_tier = "PRO"
        print(f"  (using default: {account_tier})")

    msg = input("  Enter your support message: ").strip()
    if not msg:
        msg = "My invoice shows a double charge this month"
        print(f"  (using default: {msg})")

    print_divider()
    print_input(msg)

    result = full_prompt_engineering(msg, customer_name, account_tier)

    print(f"  Category           : {result['category']}")
    print(f"  Confidence         : {result['confidence']}")
    print(f"  Action             : {result['action']}")
    print(f"  Priority           : {result['priority']}")
    print(f"  Reasoning          : {result['reasoning']}")
    print()
    print(f"  Customer Response  :")
    print(f"  {result['customer_response']}")


def run_all_levels():
    print_header("ALL LEVELS", "Running All 4 Levels Automatically")

    # Level 1
    print_header("LEVEL 1", "Basic Call — No System Prompt")
    msg = "What does a support triage agent do?"
    print_input(msg)
    print_output(simple_llm_call(msg))

    # Level 2
    print_header("LEVEL 2", "With System Prompt — Agent Identity")
    system = "You are a friendly support agent for TechCorp. Be concise."
    msg = "How do I reset my password?"
    print(f"  SYSTEM : {system}")
    print_divider()
    print_input(msg)
    print_output(llm_with_system_prompt(system, msg))

    # Level 3
    print_header("LEVEL 3", "Structured JSON Output — Ticket Classifier")
    tickets = [
        "My invoice shows a double charge",
        "App crashes when I log in",
        "Need to update my account email",
    ]
    for i, ticket in enumerate(tickets, 1):
        print()
        print(f"  TICKET {i} of {len(tickets)}")
        print_divider()
        print_input(ticket)
        result = classify_ticket(ticket)
        print(f"  Category   : {result['category']}")
        print(f"  Confidence : {result['confidence']}")
        print(f"  Action     : {result['action']}")
        print(f"  Reason     : {result['reason']}")

    # Level 4
    print_header("LEVEL 4", "All 6 Techniques — Full Prompt Engineering")
    msg = "My app keeps crashing and I have an important meeting in 1 hour"
    result = full_prompt_engineering(msg, "Kashif", "ENTERPRISE")
    print_input(msg)
    print(f"  Category           : {result['category']}")
    print(f"  Confidence         : {result['confidence']}")
    print(f"  Action             : {result['action']}")
    print(f"  Priority           : {result['priority']}")
    print(f"  Reasoning          : {result['reasoning']}")
    print()
    print(f"  Customer Response  :")
    print(f"  {result['customer_response']}")

    print()
    print("=" * 60)
    print("  ALL LEVELS COMPLETE")
    print("=" * 60)
    print()


# ─────────────────────────────────────────────────────────────
# MAIN MENU LOOP
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    while True:
        print_menu()
        choice = input("  Enter your choice (0-5): ").strip()

        if choice == "1":
            run_level_1()
        elif choice == "2":
            run_level_2()
        elif choice == "3":
            run_level_3()
        elif choice == "4":
            run_level_4()
        elif choice == "5":
            run_all_levels()
        elif choice == "0":
            print()
            print("  Exiting. See you in Session 2!")
            print()
            break
        else:
            print()
            print("  Invalid choice. Please enter a number between 0 and 5.")

        print()
        input("  Press Enter to return to the menu...")