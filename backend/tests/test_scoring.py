import pytest
from validation.scoring_engine import scoring_engine

def test_weights_sum_to_one():
    """Verify that the documented formula weights sum to exactly 1.00."""
    total_weight = sum(scoring_engine.WEIGHTS.values())
    assert round(total_weight, 6) == 1.00

def test_normal_scoring_inputs():
    """Test standard valid inputs producing an expected composite score."""
    # retrieval: 0.8 * 0.30 = 0.24
    # semantic: 0.7 * 0.25 = 0.175
    # consistency: (8.0 / 10.0) * 0.20 = 0.16
    # structural: 1.0 * 0.15 = 0.15
    # alignment: 0.5 * 0.10 = 0.05
    # Total: 0.24 + 0.175 + 0.16 + 0.15 + 0.05 = 0.775
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=0.8,
        semantic_relevance=0.7,
        consistency_score=8.0,
        structural_quality=1.0,
        memory_alignment=0.5
    )
    assert score == 0.775

def test_boundary_values_zero():
    """Test boundary where all components are minimum (0.0)."""
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=0.0,
        semantic_relevance=0.0,
        consistency_score=0.0,
        structural_quality=0.0,
        memory_alignment=0.0
    )
    assert score == 0.0

def test_boundary_values_maximum():
    """Test boundary where all components are maximum (1.0, and 10.0 for consistency)."""
    # 0.30 + 0.25 + 0.20 + 0.15 + 0.10 = 1.00
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=1.0,
        semantic_relevance=1.0,
        consistency_score=10.0,
        structural_quality=1.0,
        memory_alignment=1.0
    )
    assert score == 1.00

def test_clamping_out_of_bounds():
    """Test values exceeding maximum bounds are safely clamped to 1.0."""
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=2.5,
        semantic_relevance=5.0,
        consistency_score=100.0,
        structural_quality=3.0,
        memory_alignment=1.5
    )
    assert score == 1.0

def test_negative_values_clamped():
    """Test negative values are safely clamped to 0.0."""
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=-0.5,
        semantic_relevance=-1.0,
        consistency_score=-10.0,
        structural_quality=-0.2,
        memory_alignment=-0.5
    )
    assert score == 0.0

def test_missing_or_none_values():
    """Test None, missing, and non-numeric values do not crash and default safely."""
    score = scoring_engine.calculate_final_score(
        retrieval_similarity=None,
        semantic_relevance=None,
        consistency_score=None,
        structural_quality=None,
        memory_alignment=None
    )
    assert score == 0.0

    # Non-numeric string inputs
    components = scoring_engine.calculate_components(
        retrieval_similarity="not_a_number",
        semantic_relevance=float("nan"),
        consistency_score=None,
        structural_quality=1.0,
        memory_alignment=0.0
    )
    assert components["retrieval_similarity"] == 0.0
    assert components["semantic_relevance"] == 0.0
    assert components["structural_quality"] == 1.0
    assert components["final_score"] == 0.15
