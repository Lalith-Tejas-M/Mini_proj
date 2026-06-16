INSIGHT_SYSTEM_PROMPT = """
You are an expert sociologist and behavioral analyst.
Your goal is to generate meaningful insights based strictly on the user's topic and the historical memory provided.
You MUST use the provided memory context to ground your generation.
Compare the traditional or historical pattern to modern equivalents, and generate an actionable recommendation.
Do not hallucinate. If the memory doesn't support an insight, do your best with the raw topic, but state assumptions.
"""

INSIGHT_USER_PROMPT = """
Topic to explore: "{topic}"

Relevant Historical Memory (from our database):
{memory_context}

Based on this context, generate an insight in strict JSON format.
Schema:
{{
  "insight_text": "A comprehensive paragraph explaining the behavioral pattern or knowledge.",
  "comparison": {{
    "traditional_practice": "What they did",
    "modern_equivalent": "What we do now",
    "impact_of_shift": "Consequence of this change"
  }},
  "recommendations": {{
    "actionable_step": "One specific thing to do today based on this knowledge",
    "expected_benefit": "Why do it"
  }}
}}
"""
