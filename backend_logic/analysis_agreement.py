from backend_logic.model_provider import ai_manager

def process_contract(text: str, model: str = "flash") -> str:
    """
    Performs the initial deep analysis of the contract text.
    """
    prompt = f"""You are an expert legal AI. Analyze the following contract and provide:
1. A brief summary of the agreement.
2. Key obligations of both parties.
3. Termination clauses.
4. Any potential risks or unusual clauses.

=== CONTRACT TEXT ===
{text[:8000]}  # Truncated to avoid token limits on the first pass
"""
    return ai_manager.generate(prompt, model)