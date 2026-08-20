import os, json
from dotenv import load_dotenv
from openai import OpenAI
from tools.search_tool import TOOLS, execute_tool
from data.database import load_history
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a customer support triage agent for TechCorp.

YOUR PROCESS (follow this order every time):
Step 1: Understand what the customer is asking
Step 2: Search the FAQ using the search_faq tool
        IMPORTANT: Do NOT pass a category parameter to search_faq.
        Let semantic search find the best match across all categories.
Step 3: If FAQ search returns ANY results — use the first result to answer.
        Even a partial match is better than escalating.
Step 4: If customer mentions a ticket number → use get_ticket_status
Step 5: ONLY escalate if FAQ search returns completely empty results []

RULES YOU MUST NEVER BREAK:
- Always search the FAQ before answering — never guess
- Never invent policy information not in the FAQ
- If search_faq returns results, ALWAYS use them to answer — never escalate
- Only escalate if search_faq returns an empty list
- Be professional, empathetic, and concise
- Never pass category parameter to search_faq
- NEVER ask the customer for more details before escalating
- If you decide to escalate — call create_escalation() immediately
- Do NOT say you will escalate — just do it
- If the customer asks about a ticket already looked up in this conversation
  use the result from conversation history — do not call get_ticket_status again"""

# ── Pre-defined test cases ──────────────────────────────────
TEST_CASES = [
    "My app crashes every time I try to log in",
    "Can you check my ticket TKT-12345?",
    "I need to change my email address on the account",
    "My quantum flux capacitor sync module is broken",
]


def run_agent(user_message: str, session_id: str = "default") -> dict:
    """
    The core agentic loop — OpenAI version.
    Now with long-term memory stored in SQLite.
    """

    print(f"\n{'='*55}")
    print(f"USER: {user_message}")
    print(f"{'='*55}")

    # Load previous conversation history from SQLite
    history = load_history(session_id)
    if history:
        print(f"  [MEMORY] Loaded {len(history)} previous messages")

    # Build messages — system prompt + history + new message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,                                        # ← inject history
        {"role": "user",   "content": user_message}
    ]

    max_iterations = 5
    tools_called = []

    faq_id_returned = None

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages
        )

        message = response.choices[0].message
        print(f"finish_reason: {response.choices[0].finish_reason}")

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name  = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                tool_id    = tool_call.id
                tools_called.append(tool_name)

                print(f"  Tool called : {tool_name}")
                print(f"  With input  : {json.dumps(tool_input)}")

                result = execute_tool(tool_name, tool_input)
                print(f"  Tool result : {result[:100]}...")

                # Track which FAQ was returned for evals
                if tool_name == "search_faq":
                    try:
                        result_data = json.loads(result)
                        if result_data and len(result_data) > 0:
                            faq_id_returned = result_data[0]["id"]  # ← top FAQ ID
                    except:
                        pass

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_id,
                    "content":      result
                })

        else:
            final_answer = message.content
            return {
                "final_answer":    final_answer,
                "tools_called":    tools_called,
                "faq_id_returned": faq_id_returned  
            }

    # return "Agent reached maximum iterations. Please try again."
    return {
        "final_answer":    "Agent reached maximum iterations. Please try again.",
        "tools_called":    tools_called,
        "faq_id_returned": faq_id_returned  
    }


# ── Menu ────────────────────────────────────────────────────
def print_menu():
    print()
    print("=" * 55)
    print("  TECHCORP SUPPORT AGENT")
    print("=" * 55)
    print("  Select an option:")
    print()
    print("  1 — My app crashes every time I try to log in")
    print("  2 — Can you check my ticket TKT-12345?")
    print("  3 — I need to change my email address")
    print("  4 — My quantum flux capacitor is broken")
    print("  5 — Type my own question")
    print("  6 — Run all 4 test cases automatically")
    print("  0 — Exit")
    print()


# ── Run All Test Cases ─────────────────────────────────────
def run_all_test_cases():
    print("\n  Running all 4 test cases...\n")
    for case in TEST_CASES:
        run_agent(case)
        print("\n" + "*" * 55 + "\n")


# ── Main loop ───────────────────────────────────────────────
if __name__ == "__main__":

    while True:
        print_menu()
        choice = input("  Enter your choice (0-6): ").strip()

        if choice == "1":
            run_agent(TEST_CASES[0])

        elif choice == "2":
            run_agent(TEST_CASES[1])

        elif choice == "3":
            run_agent(TEST_CASES[2])

        elif choice == "4":
            run_agent(TEST_CASES[3])

        elif choice == "5":
            print()
            user_input = input("  Type your question: ").strip()
            if user_input:
                run_agent(user_input)
            else:
                print("  No input entered. Returning to menu.")

        elif choice == "6":
            run_all_test_cases()

        elif choice == "0":
            print()
            print("  Goodbye!")
            print()
            break

        else:
            print()
            print("  Invalid choice. Please enter a number between 0 and 6.")

        print()
        input("  Press Enter to return to the menu...")