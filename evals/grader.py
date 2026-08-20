import json
 
def rule_based_grade(test_case: dict, agent_result: dict) -> dict:
    """
    Scores agent result against expected values.
    Fast, deterministic, no API call needed.
    """
    score = 0
    max_score = 4
    details = []
 
    # Check 1: Did agent call the right tool?
    tools_called = agent_result.get("tools_called", [])
    if test_case["expected_tool"] in tools_called:
        score += 1
        details.append("✅ Correct tool called")
    else:
        details.append(f"❌ Wrong tool. Expected: {test_case['expected_tool']}, Got: {tools_called}")
 
    # Check 2: Did agent escalate when it should have?
    did_escalate = "create_escalation" in tools_called
    if did_escalate == test_case["should_escalate"]:
        score += 1
        details.append("✅ Correct escalation decision")
    else:
        details.append(f"❌ Wrong escalation. Should escalate: {test_case['should_escalate']}")
 
    # Check 3: Did agent return the right FAQ?
    if test_case["expected_faq_id"]:
        faq_returned = agent_result.get("faq_id_returned")
        if faq_returned == test_case["expected_faq_id"]:
            score += 1
            details.append("✅ Correct FAQ returned")
        else:
            details.append(f"❌ Wrong FAQ. Expected: {test_case['expected_faq_id']}, Got: {faq_returned}")
    else:
        score += 1
        details.append("✅ No FAQ expected — correct")
 
    # Check 4: Did agent provide a final answer?
    has_final_answer = bool(agent_result.get("final_answer", "").strip())
    if has_final_answer:
        score += 1
        details.append("✅ Final answer provided")
    else:
        details.append("❌ No final answer returned")
 
    return {
        "test_id":   test_case["id"],
        "score":     score,
        "max_score": max_score,
        "passed":    score == max_score,
        "details":   details
    }
 
 
def llm_judge_grade(question: str, answer: str) -> dict:
    """Uses GPT-4o to evaluate response quality."""
    from openai import OpenAI
    import os
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Rate this customer support response.
 
Customer question: {question}
Agent response: {answer}
 
Score on each criterion (1-5):
- Helpfulness: Does it actually solve the problem?
- Accuracy: Is the information correct?
- Professionalism: Is the tone appropriate?
 
Respond ONLY with JSON:
{{
  "helpfulness": 1-5,
  "accuracy": 1-5,
  "professionalism": 1-5,
  "overall": 1-5,
  "feedback": "one sentence"
}}"""
        }]
    )
    raw = response.choices[0].message.content or ""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except:
        return {
            "helpfulness": 3,
            "accuracy": 3,
            "professionalism": 3,
            "overall": 3,
            "feedback": "Could not parse LLM judge response"
        }
