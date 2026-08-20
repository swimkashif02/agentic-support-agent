import os, json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from rag.retriever import retrieve_with_rewrite
from data.database import get_tickets, get_all_escalations
load_dotenv(find_dotenv(), override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RESEARCH_SYSTEM_PROMPT = """You are a research analyst agent for TechCorp.

Your job is to analyse support data and produce structured reports.

YOUR PROCESS:
Step 1: Understand what data is needed for this specific request
Step 2: Search ONLY the relevant data sources — do not search everything every time
        - If asked about escalations → search_escalation_history()
        - If asked about tickets → search_ticket_history()
        - If asked about FAQs or known issues → search_knowledge_base()
        - If asked about everything → search all three
Step 3: Write a structured report with your findings using write_report()

RULES:
- Only call tools that are relevant to the specific request
- Do NOT search knowledge base if the user only asked about escalations
- Do NOT search tickets if the user only asked about escalations
- Always call write_report() as the final step
- Base findings only on what the tools return
- Include counts and patterns where available"""
 
# Research agent tools
RESEARCH_TOOLS = [
  {
    "type": "function",
    "function": {
      "name": "search_knowledge_base",
      "description": """Search Pinecone for FAQs related to a topic.
      Returns multiple results for research and analysis.
      Use this to find all FAQs about a subject.""",
      "parameters": {
        "type": "object",
        "properties": {
          "query":    {"type": "string"},
          "top_k":   {"type": "integer", "description": "Default 10 for research"},
          "category":{"type": "string", "enum": ["BILLING","TECHNICAL","ACCOUNT"]}
        },
        "required": ["query"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "search_ticket_history",
      "description": "Search SQLite tickets table for historical patterns.",
      "parameters": {
        "type": "object",
        "properties": {
          "status":   {"type": "string", "enum": ["OPEN","CLOSED","ALL"]},
          "subject":  {"type": "string", "description": "keyword to search"}
        },
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "search_escalation_history",
      "description": "Search SQLite escalations for patterns and trends.",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {"type": "string", "enum": ["BILLING","TECHNICAL","ACCOUNT"]},
          "priority": {"type": "string", "enum": ["LOW","MEDIUM","HIGH","URGENT"]}
        },
        "required": []
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "write_report",
      "description": """Final step — write structured report from findings.
      Call this AFTER searching. Formats findings into a clean report.""",
      "parameters": {
        "type": "object",
        "properties": {
          "title":    {"type": "string"},
          "findings": {"type": "string"},
          "summary":  {"type": "string"}
        },
        "required": ["title","findings","summary"]
      }
    }
  }
]
 
 
def execute_research_tool(tool_name: str, tool_input: dict) -> str:
    """Router for research agent tools."""
 
    if tool_name == "search_knowledge_base":
        results = retrieve_with_rewrite(
            query=tool_input["query"],
            category=tool_input.get("category")
        )
        return json.dumps(results)
 
    elif tool_name == "search_ticket_history":
        status  = tool_input.get("status", "ALL")
        subject = tool_input.get("subject", "")
        rows = get_tickets(status=status, subject=subject)
        return json.dumps(rows)
 
    elif tool_name == "search_escalation_history":
        category = tool_input.get("category")
        rows = get_all_escalations(category=category)
        return json.dumps(rows)
 
    elif tool_name == "write_report":
        report = f"""
                # {tool_input["title"]}
                
                ## Findings
                {tool_input["findings"]}
                
                ## Summary
                {tool_input["summary"]}
                """
        return json.dumps({"report": report, "status": "COMPLETE"})
 
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
 
 
def run_research(user_message: str) -> str:
    """Research agent agentic loop — same pattern as triage agent."""

    print(f"\n{'='*55}")
    print(f"RESEARCH AGENT: {user_message}")
    print(f"{'='*55}")

    messages = [
        {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
        {"role": "user",   "content": user_message}
    ]

    for iteration in range(5):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            tools=RESEARCH_TOOLS,
            messages=messages
        )
        message = response.choices[0].message
        print(f"finish_reason: {response.choices[0].finish_reason}")

        if message.tool_calls:
            messages.append(message)
            for tc in message.tool_calls:
                tool_name  = tc.function.name
                tool_input = json.loads(tc.function.arguments)

                print(f"  Tool called : {tool_name}")
                print(f"  With input  : {json.dumps(tool_input)}")

                result = execute_research_tool(tool_name, tool_input)
                print(f"  Tool result : {result[:120]}...")

                messages.append({
                    "role":         "tool",
                    "tool_call_id": tc.id,
                    "content":      result
                })
        else:
            print(f"\nRESEARCH COMPLETE")
            return message.content

    return "Research agent reached max iterations."
