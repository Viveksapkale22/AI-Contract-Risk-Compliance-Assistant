from backend_logic.model_provider import ai_manager

def process_contract(text: str, model: str = "flash") -> str:
    """
    Performs the initial deep analysis of the contract text.
    """
    # --- BUG FIX: Define context_text here! ---
    clean_text = " ".join(text.split())
    context_text = clean_text[:15000] # Safe limit for Gemini API
    # ------------------------------------------

    prompt = f"""
You are an expert, pragmatic legal advisor. Your goal is to help the user understand their contract constructively. 

Do not be overly alarmist. Differentiate between standard business imbalances and actual predatory traps.

---
STRICT RULES:
- Use ONLY information from the contract. Do not hallucinate.
- If standard boilerplate is missing, treat it as a "Recommendation" to improve the contract, NOT a critical Red Flag.
- Keep the language simple, professional, and actionable.

---
ANALYSIS INSTRUCTIONS:

1. 📄 CONTRACT OVERVIEW:
- 3–4 bullet points explaining the core agreement (Parties, Purpose, Key Deliverables).

2. ⚖️ KEY CLAUSES EXPLAINED:
- Briefly explain Payment, Timeline, Liability, and Termination in plain English.

3. 🚨 CRITICAL RED FLAGS (Only if applicable):
- ONLY list severe, predatory, or highly dangerous clauses here.
- Examples of Red Flags: Unlimited financial liability, completely one-sided termination, illegal penalties, loss of core Intellectual Property.
- If there are no severe traps, write: "No severe red flags detected."

4. ⚠️ AREAS OF CONCERN (Medium Risk):
- Highlight unbalanced terms or standard loopholes that favor the other party.
- Example: Vague deadlines, auto-renewals without notice, or low liability caps.

5. 💡 CONSTRUCTIVE RECOMMENDATIONS & NEGOTIATION TACTICS:
- List standard clauses that are missing and suggest adding them to protect the user.
- For EVERY recommendation, provide a brief, actionable "Negotiation Tip."
- Instead of just saying "Add a grace period," tell the user exactly what to ask for (e.g., "Request a 15-day grace period to prevent accidental service lockouts").
- Give the user practical advice on how to push back on unfair terms politely.

6. 📊 FINAL RISK ASSESSMENT:
- Grade the contract strictly based on this scale:
  * LOW RISK: Balanced terms, standard industry practice.
  * MEDIUM RISK: Contains unbalanced terms or is missing standard protections, but no predatory traps. (Most standard contracts fall here).
  * HIGH RISK: Contains predatory traps, unlimited liability, or severe legal exposure for the user.
- Provide a 2-sentence justification for the grade.

---
Contract Text:
{context_text}
"""
    return ai_manager.generate(prompt, model)