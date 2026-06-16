class RulesLayer:
    """Deterministic business logic rules for Insight Validation."""
    
    def check_length(self, insight_json: dict) -> tuple[bool, str]:
        text = insight_json.get("insight_text", "")
        if len(text.split()) < 30:
            return False, "Insight text is too short (under 30 words)."
        return True, ""
        
    def check_structure(self, insight_json: dict) -> tuple[bool, str]:
        required_keys = ["insight_text", "comparison", "recommendations"]
        for key in required_keys:
            if key not in insight_json:
                return False, f"Missing required structural key: {key}"
                
        comp = insight_json.get("comparison", {})
        if not all(k in comp for k in ["traditional_practice", "modern_equivalent", "impact_of_shift"]):
            return False, "Comparison block is missing required fields."
            
        rec = insight_json.get("recommendations", {})
        if not all(k in rec for k in ["actionable_step", "expected_benefit"]):
            return False, "Recommendations block is missing required fields."
            
        return True, ""
        
    def check_generic_phrases(self, insight_json: dict) -> tuple[bool, str]:
        generic_phrases = ["be better", "do good", "be mindful", "pay attention", "just a thought"]
        rec = insight_json.get("recommendations", {}).get("actionable_step", "").lower()
        
        for phrase in generic_phrases:
            if phrase in rec:
                return False, f"Recommendation contains generic fluff phrase: '{phrase}'. Must be highly actionable."
                
        return True, ""

    def validate_all(self, insight_json: dict) -> tuple[bool, str]:
        """Run all deterministic rules."""
        checks = [self.check_structure, self.check_length, self.check_generic_phrases]
        
        for check in checks:
            passed, reason = check(insight_json)
            if not passed:
                return False, reason
                
        return True, ""

rules_layer = RulesLayer()
