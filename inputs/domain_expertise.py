DOMAIN_EXPERTISE = {
    # --------------------------------------------------
    # Core identity
    # --------------------------------------------------
    "agent_type": "mathematical",
    "domain": "math",

    # --------------------------------------------------
    # What the agent CAN do
    # --------------------------------------------------
    "capabilities": [
        "arithmetic",          # +, -, *, /
        "algebra",             # linear / quadratic equations (numeric)
        "geometry",            # area, volume, perimeter
        "approximation",       # π ≈ 3.14, e ≈ 2.718
        "error_handling"       # detect ambiguity / insufficient info
    ],

    # --------------------------------------------------
    # What the agent CANNOT do (CRITICAL)
    # --------------------------------------------------
    "limitations": [
        "symbolic_math",       # no expressions like ±√(25 - x^2)
        "multi_variable_free_form",
        "formal_proofs"
    ],

    # --------------------------------------------------
    # Evaluation rules (used by evaluator + dataset author)
    # --------------------------------------------------
    "evaluation_policy": {
        # Numeric tolerance for approximate answers
        "numeric_tolerance": 0.3,

        # If prompt has multiple variables with no values,
        # expected behavior is to REFUSE
        "require_numeric_values": True,

        # Symbolic answers are NOT expected
        "symbolic_output_allowed": False
    }
}
