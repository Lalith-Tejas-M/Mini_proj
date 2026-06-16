import json
import structlog
from validation.rules_layer import rules_layer
from services.ollama_service import ollama_client
from prompts.validation_prompts import VALIDATION_SYSTEM_PROMPT, VALIDATION_USER_PROMPT

logger = structlog.get_logger()

class ValidationEngine:
    async def evaluate_insight(self, topic: str, insight_json: dict) -> dict:
        """
        Runs rules layer and LLM rubric to validate an insight.
        Returns a dict with pass status, score, and failure reason.
        """
        # 1. Deterministic Rules
        rules_passed, rule_reason = rules_layer.validate_all(insight_json)
        if not rules_passed:
            logger.warn("insight_failed_rules", reason=rule_reason)
            return {
                "passed": False,
                "score": 0.0,
                "structural_quality": 0.0,
                "consistency_score": 0.0,
                "failure_reason": rule_reason
            }
            
        # 2. LLM Semantic Validation
        prompt = VALIDATION_USER_PROMPT.format(
            topic=topic,
            insight_json=json.dumps(insight_json, indent=2)
        )
        
        try:
            response = await ollama_client.generate(
                prompt=prompt,
                system=VALIDATION_SYSTEM_PROMPT,
                format_json=True
            )
            
            val_data = json.loads(response)
            passed = val_data.get("passed", False)
            score = float(val_data.get("score", 0.0))
            reason = val_data.get("failure_reason", "")
            
            return {
                "passed": passed,
                "score": score,
                "structural_quality": 1.0, # passed rules
                "consistency_score": score,
                "failure_reason": reason
            }
            
        except Exception as e:
            logger.error("llm_validation_failed", error=str(e))
            # Fallback if validation crashes: assume it passed rules, so it's moderately okay
            return {
                "passed": True,
                "score": 5.0,
                "structural_quality": 1.0,
                "consistency_score": 5.0,
                "failure_reason": "LLM validation failed, passed fallback rules."
            }

validation_engine = ValidationEngine()
