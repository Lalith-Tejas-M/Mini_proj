import math
from typing import Dict, Any, Optional

class ScoringEngine:
    """
    Computes a composite weighted heuristic confidence score (0.0 to 1.0).
    Total weight equals exactly 1.00:
      - 0.30 x retrieval_similarity (clamped 0.0 to 1.0)
      - 0.25 x semantic_relevance  (clamped 0.0 to 1.0)
      - 0.20 x consistency_score   (input 0.0 to 10.0, normalized / 10.0, clamped 0.0 to 1.0)
      - 0.15 x structural_quality  (clamped 0.0 to 1.0)
      - 0.10 x memory_alignment   (clamped 0.0 to 1.0)

    Note: This is a deterministic composite scoring heuristic, not an empirically
    calibrated Bayesian probability distribution.
    """

    WEIGHTS = {
        "retrieval_similarity": 0.30,
        "semantic_relevance": 0.25,
        "consistency": 0.20,
        "structural_quality": 0.15,
        "memory_alignment": 0.10,
    }

    def _sanitize_float(self, value: Any, default: float = 0.0, min_val: float = 0.0, max_val: float = 1.0) -> float:
        if value is None:
            return default
        try:
            val = float(value)
            if math.isnan(val) or math.isinf(val):
                return default
            return max(min_val, min(max_val, val))
        except (ValueError, TypeError):
            return default

    def calculate_components(
        self,
        retrieval_similarity: Optional[float] = 0.0,
        semantic_relevance: Optional[float] = 0.0,
        consistency_score: Optional[float] = 0.0,
        structural_quality: Optional[float] = 0.0,
        memory_alignment: Optional[float] = 0.0
    ) -> Dict[str, float]:
        """Calculates both the sanitized component scores and the final composite score."""
        sim = self._sanitize_float(retrieval_similarity, 0.0, 0.0, 1.0)
        sem = self._sanitize_float(semantic_relevance, 0.0, 0.0, 1.0)
        
        # Consistency score is on a 0-10 scale from LLM rubric
        raw_cons = self._sanitize_float(consistency_score, 0.0, 0.0, 10.0)
        norm_consistency = raw_cons / 10.0
        
        sq = self._sanitize_float(structural_quality, 0.0, 0.0, 1.0)
        mem = self._sanitize_float(memory_alignment, 0.0, 0.0, 1.0)

        final_score = (
            (self.WEIGHTS["retrieval_similarity"] * sim) +
            (self.WEIGHTS["semantic_relevance"] * sem) +
            (self.WEIGHTS["consistency"] * norm_consistency) +
            (self.WEIGHTS["structural_quality"] * sq) +
            (self.WEIGHTS["memory_alignment"] * mem)
        )

        clamped_final = max(0.0, min(1.0, round(final_score, 4)))

        return {
            "retrieval_similarity": round(sim, 4),
            "semantic_relevance": round(sem, 4),
            "consistency_score": round(raw_cons, 4),
            "normalized_consistency": round(norm_consistency, 4),
            "structural_quality": round(sq, 4),
            "memory_alignment": round(mem, 4),
            "final_score": clamped_final
        }

    def calculate_final_score(
        self,
        retrieval_similarity: Optional[float] = 0.0,
        semantic_relevance: Optional[float] = 0.0,
        consistency_score: Optional[float] = 0.0,
        structural_quality: Optional[float] = 0.0,
        memory_alignment: Optional[float] = 0.0
    ) -> float:
        components = self.calculate_components(
            retrieval_similarity=retrieval_similarity,
            semantic_relevance=semantic_relevance,
            consistency_score=consistency_score,
            structural_quality=structural_quality,
            memory_alignment=memory_alignment
        )
        return components["final_score"]

scoring_engine = ScoringEngine()
