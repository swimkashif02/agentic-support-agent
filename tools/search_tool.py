import json, random
 
FAQ_DATABASE = [

    # ── TECHNICAL ──────────────────────────────────────────────
    {"id": "faq-001", "category": "TECHNICAL",
     "question": "App crashes on login",
     "answer": "Clear app cache and cookies. Update to the latest app version. If issue persists, uninstall and reinstall the app. Contact support if problem continues after reinstall."},

    {"id": "faq-002", "category": "TECHNICAL",
     "question": "Password reset email not received",
     "answer": "Check your spam and junk folders. Password reset links expire after 15 minutes — request a new one if expired. Ensure you are checking the email address registered to your account."},

    {"id": "faq-003", "category": "TECHNICAL",
     "question": "App is running slowly or freezing",
     "answer": "Close all background apps and restart the device. Ensure you have at least 1GB of free storage. Update to the latest app version. If issue continues, uninstall and reinstall."},

    {"id": "faq-004", "category": "TECHNICAL",
     "question": "Cannot connect to the internet or server error",
     "answer": "Check your internet connection. Try switching between WiFi and mobile data. If the problem affects all users, check our status page at status.techcorp.com for ongoing incidents."},

    {"id": "faq-005", "category": "TECHNICAL",
     "question": "Two factor authentication code not working",
     "answer": "Ensure your device clock is set to automatic time sync. Authenticator codes are time-sensitive and expire every 30 seconds. If locked out, use your backup codes or contact support."},

    {"id": "faq-006", "category": "TECHNICAL",
     "question": "App not available in my country or region",
     "answer": "TechCorp is currently available in 45 countries. Visit techcorp.com/regions for the full list. If your region is not supported, you can join our waitlist at techcorp.com/waitlist."},

    {"id": "faq-007", "category": "TECHNICAL",
     "question": "Cannot upload files or attachments",
     "answer": "Maximum file size is 25MB. Supported formats are PDF, JPG, PNG, DOCX, and XLSX. Ensure you have a stable internet connection during upload. Try a different browser if issue persists."},

    # ── BILLING ────────────────────────────────────────────────
    {"id": "faq-008", "category": "BILLING",
     "question": "Double charge on invoice",
     "answer": "Duplicate charges are detected automatically and reversed within 3-5 business days. Check your bank statement after 5 days. If not resolved, contact billing support with your invoice number."},

    {"id": "faq-009", "category": "BILLING",
     "question": "How to cancel subscription",
     "answer": "Go to Settings > Billing > Cancel Plan. You keep full access until the end of your current billing period. No refund is issued for partial months. Cancellation takes effect at next renewal date."},

    {"id": "faq-010", "category": "BILLING",
     "question": "How to upgrade or downgrade my plan",
     "answer": "Go to Settings > Billing > Change Plan. Upgrades take effect immediately and are prorated. Downgrades take effect at the next billing cycle. You will receive a confirmation email after any plan change."},

    {"id": "faq-011", "category": "BILLING",
     "question": "Which payment methods are accepted",
     "answer": "We accept Visa, Mastercard, American Express, PayPal, and bank transfers for annual plans. Cryptocurrency and cash payments are not accepted. All transactions are secured with 256-bit encryption."},

    {"id": "faq-012", "category": "BILLING",
     "question": "How to get a refund",
     "answer": "Refunds are available within 14 days of purchase for annual plans only. Monthly plans are non-refundable. To request a refund, contact billing support with your order number and reason for refund."},

    {"id": "faq-013", "category": "BILLING",
     "question": "How to download or print an invoice",
     "answer": "Go to Settings > Billing > Invoice History. Select the invoice you need and click Download PDF. Invoices are available for all transactions in the last 24 months."},

    {"id": "faq-014", "category": "BILLING",
     "question": "Why was my payment declined",
     "answer": "Common reasons: insufficient funds, card expired, billing address mismatch, or bank blocking international transactions. Update your payment method in Settings > Billing or contact your bank to authorise the transaction."},

    # ── ACCOUNT ────────────────────────────────────────────────
    {"id": "faq-015", "category": "ACCOUNT",
     "question": "How to change account email",
     "answer": "Go to Settings > Profile > Email Address. Click Edit and enter your new email. A verification link is sent to both old and new addresses. Click the link in the new email to confirm the change."},

    {"id": "faq-016", "category": "ACCOUNT",
     "question": "How to change account password",
     "answer": "Go to Settings > Security > Change Password. Enter your current password then your new password twice. Password must be at least 8 characters and include one number and one special character."},

    {"id": "faq-017", "category": "ACCOUNT",
     "question": "How to delete my account permanently",
     "answer": "Go to Settings > Account > Delete Account. You will be asked to confirm by entering your password. Account deletion is permanent and cannot be undone. All data is removed within 30 days per our privacy policy."},

    {"id": "faq-018", "category": "ACCOUNT",
     "question": "How to add or remove team members",
     "answer": "Go to Settings > Team > Manage Members. Click Invite to add a new member by email. To remove a member, click the three dots next to their name and select Remove. Changes take effect immediately."},

    {"id": "faq-019", "category": "ACCOUNT",
     "question": "How to update billing address or company name",
     "answer": "Go to Settings > Billing > Billing Information. Click Edit to update your company name, address, or VAT number. Updated information appears on all future invoices. Past invoices cannot be modified."},

    {"id": "faq-020", "category": "ACCOUNT",
     "question": "How to enable or disable email notifications",
     "answer": "Go to Settings > Notifications > Email Preferences. Toggle individual notification types on or off. Changes are saved automatically. You can also unsubscribe from marketing emails at the bottom of any email we send."},
] 


TOOLS = [
 
  # ── TOOL 1: Search the FAQ knowledge base ──────────────────
  {
    "type": "function",       # ← Required by OpenAI API
    "function": {
      "name": "search_faq",
      "description": """Search the company FAQ knowledge base for
      relevant help articles. Use this when the customer asks a
      question that might be in company documentation.""",
      "parameters": {         # ← "parameters" in OpenAI (not "input_schema")
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The search query using customer's key words"
          },
          "category": {
            "type": "string",
            "enum": ["BILLING", "TECHNICAL", "ACCOUNT", "GENERAL"],
            "description": "Optional: filter results by category"
          },
          "max_results": {
            "type": "integer",
            "description": "Max FAQ entries to return. Default: 3"
          }
        },
        "required": ["query"]
      }
    }
  },
 
  # ── TOOL 2: Get ticket status ───────────────────────────────
  {
    "type": "function",
    "function": {
      "name": "get_ticket_status",
      "description": """Retrieve status of an existing support ticket.
      Use when customer mentions a ticket number (format: TKT-XXXXX).""",
      "parameters": {
        "type": "object",
        "properties": {
          "ticket_id": {
            "type": "string",
            "description": "The ticket ID. Example: TKT-12345"
          }
        },
        "required": ["ticket_id"]
      }
    }
  },
 
  # ── TOOL 3: Create escalation ────────────────────────────────
  {
    "type": "function",
    "function": {
      "name": "create_escalation",
      "description": """Create an escalation when agent cannot resolve
      the issue with available FAQ information. Use for complex issues
      requiring human review. Do NOT use if a clear FAQ answer exists.""",
      "parameters": {
        "type": "object",
        "properties": {
          "summary": { "type": "string" },
          "category": { "enum": ["BILLING","TECHNICAL","ACCOUNT"] },
          "priority": { "enum": ["LOW","MEDIUM","HIGH","URGENT"] }
        },
        "required": ["summary","category","priority"]
      }
    }
  }
]


def search_faq(query: str, category: str = None, max_results: int = 3) -> list:
    """Keyword search — replaced by semantic Vector DB search in Week 2."""
    query_words = query.lower().split()
    results = []
    for faq in FAQ_DATABASE:
        if category and faq["category"] != category:
            continue
        text = (faq["question"] + " " + faq["answer"]).lower()
        score = sum(1 for word in query_words if word in text)
        if score > 0:
            results.append({**faq, "relevance_score": score})
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:max_results]
 
 
def get_ticket_status(ticket_id: str) -> dict:
    return {"ticket_id":ticket_id,"status":"OPEN",
            "subject":"Login issue reported","assigned_to":"Support Team A"}
 
 
def create_escalation(summary: str, category: str, priority: str) -> dict:
    eid = f"ESC-{random.randint(10000,99999)}"
    return {"escalation_id":eid,"status":"CREATED",
            "message":f"Escalation {eid} created. Team responds within 4 hours."}
 


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Router: maps LLM tool request to real Python function."""
    if tool_name == "search_faq":
        return json.dumps(search_faq(**tool_input))
    elif tool_name == "get_ticket_status":
        return json.dumps(get_ticket_status(**tool_input))
    elif tool_name == "create_escalation":
        return json.dumps(create_escalation(**tool_input))
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
