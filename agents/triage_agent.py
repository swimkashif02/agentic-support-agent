import os, json
from dotenv import load_dotenv
from openai import OpenAI
from tools.search_tool import TOOLS, execute_tool

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """You are a customer support triage agent for TechCorp.

YOUR PROCESS (follow this order every time):
Step 1: Understand what the customer is asking
Step 2: Search the FAQ using the search_faq tool
Step 3: If FAQ has a clear answer → respond directly with it
Step 4: If customer mentions a ticket number → use get_ticket_status
Step 5: If you cannot find a clear answer → use create_escalation

RULES YOU MUST NEVER BREAK:
- Always search the FAQ before answering — never guess
- Never invent policy information not in the FAQ
- If FAQ returns no relevant results, always escalate
- Be professional, empathetic, and concise"""


# ── Pre-defined test cases ──────────────────────────────────
TEST_CASES = [
    "My app crashes every time I try to log in",
    "Can you check my ticket TKT-12345?",
    "I need to change my email address on the account",
    "My quantum flux capacitor sync module is broken",
]


def run_agent(user_message: str) -> str:
    """
    The core agentic loop — OpenAI version.
    Runs until message.tool_calls is None (final answer).
    Safety limit of 5 iterations prevents infinite loops.
    """

    print(f"\n{'='*55}")
    print(f"USER: {user_message}")
    print(f"{'='*55}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message}
    ]

    max_iterations = 5

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

                print(f"  Tool called : {tool_name}")
                print(f"  With input  : {json.dumps(tool_input)}")

                result = execute_tool(tool_name, tool_input)
                print(f"  Tool result : {result[:100]}...")

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_id,
                    "content":      result
                })

        else:
            final_answer = message.content
            print(f"\nFINAL ANSWER:\n{final_answer}")
            return final_answer

    return "Agent reached maximum iterations. Please try again."


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