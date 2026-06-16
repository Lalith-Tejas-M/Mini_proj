import json
import structlog
from prompts.insight_prompts import INSIGHT_SYSTEM_PROMPT, INSIGHT_USER_PROMPT
from prompts.regeneration_prompts import REGENERATION_SYSTEM_PROMPT, REGENERATION_USER_PROMPT
from services.ollama_service import ollama_client
from memory.memory_manager import memory_manager
from validation.validation_engine import validation_engine
from validation.scoring_engine import scoring_engine
from services.personalization_service import personalization_service

logger = structlog.get_logger()

class InsightAgent:
    async def generate_insight(self, topic: str, user_id: str) -> dict:
        """
        1. Retrieve memory context (RAG)
        2. Generate insight
        3. Validate insight
        4. Regenerate if failed (max 3 tries)
        5. Score and return
        """
        # 1. RAG Memory Retrieval
        memory_results = await memory_manager.retrieve_similar(topic, top_k=3)
        memory_context = ""
        retrieval_sim = 0.0
        if memory_results:
            retrieval_sim = memory_results[0].get("similarity_score", 0.0)
            for m in memory_results:
                memory_context += f"- Pattern: {m.get('pattern', '')}. Snippet: {m.get('raw_snippet', '')}\n"
        else:
            memory_context = "No historical memory found for this topic."

        # 1.b Personalization injection
        user_context = await personalization_service.get_user_context(user_id)
        if user_context:
            memory_context += f"\n\nPersonalization Guidelines:\n{user_context}"

        # 2. Initial Generation
        prompt = INSIGHT_USER_PROMPT.format(topic=topic, memory_context=memory_context)
        
        insight_json = await self._call_llm(prompt, INSIGHT_SYSTEM_PROMPT)
        
        # 3. Validation & Regeneration Loop
        max_retries = 3
        attempts = 0
        final_validation = None
        
        while attempts < max_retries:
            attempts += 1
            logger.info("insight_validation_attempt", attempt=attempts)
            
            final_validation = await validation_engine.evaluate_insight(topic, insight_json)
            
            if final_validation["passed"]:
                break
                
            logger.warn("insight_rejected", reason=final_validation["failure_reason"])
            
            # Regenerate
            regen_prompt = REGENERATION_USER_PROMPT.format(
                topic=topic,
                failure_reason=final_validation["failure_reason"],
                rejected_json=json.dumps(insight_json)
            )
            insight_json = await self._call_llm(regen_prompt, REGENERATION_SYSTEM_PROMPT)

        # 4. Final Scoring
        # Memory alignment heuristic: rough overlap of words between memory context and generated text
        mem_words = set(memory_context.lower().split())
        out_words = set(json.dumps(insight_json).lower().split())
        overlap = len(mem_words.intersection(out_words)) / max(1, len(mem_words)) if memory_results else 0.0
        
        final_score = scoring_engine.calculate_final_score(
            retrieval_similarity=retrieval_sim,
            semantic_relevance=retrieval_sim * 0.9, # approximation
            consistency_score=final_validation.get("consistency_score", 0.0),
            structural_quality=final_validation.get("structural_quality", 0.0),
            memory_alignment=min(1.0, overlap * 2.0)
        )
        
        return {
            "insight": insight_json,
            "validation": final_validation,
            "final_score": final_score,
            "attempts": attempts,
            "memory_used": len(memory_results) > 0
        }

    async def _call_llm(self, prompt: str, system: str) -> dict:
        try:
            response = await ollama_client.generate(prompt=prompt, system=system, format_json=True)
            return json.loads(response)
        except json.JSONDecodeError:
            return {} # Will naturally fail structure validation

insight_agent = InsightAgent()
