REGENERATION_SYSTEM_PROMPT = """
You are a senior behavioral analyst correcting a junior analyst's work.
The previous insight generated was rejected during validation.
Your job is to fix the issues and generate a much better, stricter response in the exact same JSON format.
"""

REGENERATION_USER_PROMPT = """
We attempted to generate an insight for the topic: "{topic}"
However, the validation engine rejected it for the following reason:
"{failure_reason}"

Original rejected output:
{rejected_json}

Please rewrite the insight to specifically fix these issues. Make it more specific, grounded, and logical.
Return ONLY valid JSON matching the schema:
{{
  "insight_text": "...",
  "comparison": {{
    "traditional_practice": "...",
    "modern_equivalent": "...",
    "impact_of_shift": "..."
  }},
  "recommendations": {{
    "actionable_step": "...",
    "expected_benefit": "..."
  }}
}}
"""
