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
        Returns a dict with pass status, explicit validation status, score, and failure reason.
        """
        # 1. Deterministic Rules
        rules_passed, rule_reason = rules_layer.validate_all(insight_json)
        if not rules_passed:
            logger.warn("insight_failed_rules", reason=rule_reason)
            return {
                "passed": False,
                "status": "validation_failed",
                "validation_status": "validation_failed",
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
        except Exception as e:
            logger.error("auditor_call_failed", error=str(e))
            return {
                "passed": False,
                "status": "validation_unavailable",
                "validation_status": "validation_unavailable",
                "score": 0.0,
                "structural_quality": 1.0, # passed deterministic rules
                "consistency_score": 0.0,
                "failure_reason": f"Auditor unavailable: {str(e)}"
            }

        try:
            val_data = json.loads(response)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("auditor_malformed_json", error=str(e), response=response)
            return {
                "passed": False,
                "status": "validation_unavailable",
                "validation_status": "validation_unavailable",
                "score": 0.0,
                "structural_quality": 1.0,
                "consistency_score": 0.0,
                "failure_reason": f"Auditor output was malformed JSON: {str(e)}"
            }
            
        passed = bool(val_data.get("passed", False))
        try:
            score = float(val_data.get("score", 0.0))
        except (ValueError, TypeError):
            score = 0.0
        reason = val_data.get("failure_reason", "")
        if not passed and not reason:
            reason = "Auditor rejected insight based on evaluation rubric."

        return {
            "passed": passed,
            "status": "validated" if passed else "validation_failed",
            "validation_status": "validated" if passed else "validation_failed",
            "score": score,
            "structural_quality": 1.0,
            "consistency_score": score,
            "failure_reason": "" if passed else reason
        }

validation_engine = ValidationEngine()
