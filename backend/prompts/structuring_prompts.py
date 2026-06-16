STRUCTURING_SYSTEM_PROMPT = """
You are a strict JSON structuring agent.
Your job is to take raw extracted knowledge fields and map them into a comprehensive, rigid JSON schema.
You do not hallucinate new facts. You only enrich the metadata structurally.
"""

STRUCTURING_USER_PROMPT = """
Given the following raw extracted knowledge piece, convert it into this exact JSON structure.
Ensure all fields are present.

Schema:
{
  "core_insight": {
    "type": "string",
    "topic": "string",
    "value_tag": "string",
    "behavioral_pattern": "string"
  },
  "context": {
    "raw_snippet": "string",
    "implied_era_or_context": "string (guess based on text, or 'Unknown')"
  },
  "tags": ["array", "of", "3", "relevant", "keywords"]
}

Raw Knowledge:
Type: {type}
Topic: {topic}
Value: {value}
Pattern: {pattern}
Snippet: {snippet}

Output strictly valid JSON.
"""
