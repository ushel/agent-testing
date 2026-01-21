def validate_dataset(dataset: dict):
    # ------------------------------
    # Dataset-level checks
    # ------------------------------
    for key in ["dataset_name", "intent", "agent_type", "rows", "evaluation_rules"]:
        if key not in dataset:
            raise ValueError(f"Dataset missing required key: {key}")

    if not isinstance(dataset["rows"], list):
        raise ValueError("rows must be a list")

    if len(dataset["rows"]) < 10:
        raise ValueError("Dataset must contain at least 10 rows")

    # ------------------------------
    # Row-level semantic checks
    # (NOT structural ones)
    # ------------------------------
    for i, row in enumerate(dataset["rows"]):
        # These MUST exist and MUST NOT be auto-invented
        if not row.get("input_prompt"):
            raise ValueError(f"Row {i} has empty or missing input_prompt")

        if not row.get("expected_output"):
            raise ValueError(f"Row {i} has empty or missing expected_output")

        if row.get("difficulty") not in {"easy", "medium", "hard"}:
            raise ValueError(f"Row {i} has invalid difficulty")

        # expected_tools is GUARANTEED by normalizer
        if not isinstance(row["expected_tools"], list):
            raise ValueError(f"Row {i} expected_tools must be a list")
