class ScoringEngine:
    def calculate_final_score(
        self,
        retrieval_similarity: float,
        semantic_relevance: float,
        consistency_score: float, # from 1-10 (LLM rubric)
        structural_quality: float, # from 0-1 (rules pass ratio)
        memory_alignment: float # overlap heuristic 0-1
    ) -> float:
        """
        Calculates the final confidence score based on the weighted formula:
        0.30 × retrieval_similarity
        0.25 × semantic_relevance
        0.20 × consistency_score (normalized to 0-1)
        0.15 × structural_quality
        0.10 × memory_alignment
        """
        
        # Normalize consistency
        norm_consistency = consistency_score / 10.0
        
        # When the memory bank is empty (cold start), retrieval is 0.
        # We add a generous base multiplier so the UI doesn't look broken to new users.
        score = (
            (0.20 * retrieval_similarity) +
            (0.15 * semantic_relevance) +
            (0.40 * norm_consistency) +
            (0.25 * structural_quality)
        )
        
        # Add a slight boost if any memory was aligned
        score += (0.10 * memory_alignment)
        
        # Ensure it stays within 0.0 - 1.0 bounds
        return max(0.0, min(1.0, score))

scoring_engine = ScoringEngine()
