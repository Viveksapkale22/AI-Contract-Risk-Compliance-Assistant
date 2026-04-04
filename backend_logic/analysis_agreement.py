from backend_logic.model_provider import ai_manager

def process_contract(text: str, model: str = "flash") -> str:
    """
    Performs the initial deep analysis of the contract text.
    """
    prompt =  prompt = f"""
You are an expert legal contract analysis assistant.

Your job is to analyze the given contract deeply from a real-world legal and risk perspective.

---

IMPORTANT RULES (STRICT):
- Use ONLY information from the contract
- Do NOT assume or hallucinate
- If something is missing, clearly say: "Not specified"
- Be practical, realistic, and user-focused
- Avoid generic or vague statements

---

ANALYSIS INSTRUCTIONS:

1. CONTRACT OVERVIEW:
- Explain what the contract is about in 3–5 clear bullet points

---

2. KEY CLAUSES:
- Identify important clauses such as:
  Payment, Scope of Work, Timeline, Liability, Termination, Confidentiality, etc.
- Explain each clause in simple language

---

3. RISK ANALYSIS:
- Identify real-world risks for the user
- Mention financial, legal, and operational risks
- Clearly explain the impact of each risk

---

4. RED FLAGS (VERY IMPORTANT):
- Highlight dangerous or unclear terms
- Examples:
  - No refund policy
  - Unlimited liability
  - Vague deadlines
  - One-sided terms

---

5. ISSUES (SEPARATE VIEW):

Client Side Issues:
- List problems affecting the client

Contractor Side Issues:
- List problems affecting the contractor

---

6. RECOMMENDATIONS:
- Give practical improvements
- Suggestions should be actionable
- Focus on making the contract safer and clearer

---

7. MISSING CLAUSES:
- List important clauses that are not present but should be included
- Examples:
  - Dispute resolution
  - Data protection
  - Intellectual property
  - SLA (Service Level Agreement)
  - Penalty clauses

---

8. FINAL RISK SUMMARY:
- Overall Risk Level: Low / Medium / High
- Give a short reason for this rating

---

Contract:
{text}
  """ 
    return ai_manager.generate(prompt, model)