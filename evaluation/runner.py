# --------------------------------------------------
# Evaluation Runner (Tool-Aware, Stable)
# --------------------------------------------------

import re
from typing import Callable, Tuple, List, Dict, Any


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _extract_number(text: str):
    if not text:
        return None
    match = re.search(r"-?\d+(\.\d+)?", text)
    return float(match.group()) if match else None


def _normalize(text: str) -> str:
    return str(text).strip().lower()


def is_correct(expected: str, actual: str, tolerance: float = 0.3) -> bool:
    if not actual:
        return False

    exp = _normalize(expected)
    act = _normalize(actual)

    # Exact / substring
    if exp == act or exp in act or act in exp:
        return True

    # Numeric tolerance
    exp_num = _extract_number(exp)
    act_num = _extract_number(act)
    if exp_num is not None and act_num is not None:
        if abs(exp_num - act_num) <= tolerance:
            return True

    # Approximate answers
    if "approx" in exp and exp_num is not None and act_num is not None:
        return True

    return False


# --------------------------------------------------
# Main Evaluation Loop
# --------------------------------------------------
def evaluate(
    agent_fn: Callable[[str], Any],
    dataset: dict,
    verbose: bool = True
) -> Tuple[float, List[Dict]]:
    """
    Agent return contract (preferred):
    {
        "output": str,
        "tools_called": List[str]
    }

    Legacy agents returning strings are supported.
    """

    rows = dataset["rows"]
    rules = dataset.get("evaluation_rules", {})

    tolerance = rules.get("numeric_tolerance", 0.3)
    tool_weight = rules.get("tool_accuracy_weight", 0.5)
    response_weight = rules.get("response_accuracy_weight", 0.5)

    tool_correct = 0
    response_correct = 0

    results = []

    if verbose:
        print("\nRunning Evaluation\n")

    for i, row in enumerate(rows):
        prompt = row["input_prompt"]
        expected_output = row["expected_output"]
        expected_tools = set(row.get("expected_tools", []))

        # -----------------------------
        # Run agent
        # -----------------------------
        try:
            raw = agent_fn(prompt)

            if isinstance(raw, dict):
                actual_output = raw.get("output")
                actual_tools = set(raw.get("tools_called", []))
            else:
                actual_output = str(raw)
                actual_tools = set()

        except Exception as e:
            actual_output = f"error: {e}"
            actual_tools = set()

        # -----------------------------
        # Tool evaluation
        # -----------------------------
        tool_expected = len(expected_tools) > 0
        tool_called = len(actual_tools) > 0

        if tool_expected:
            correct_tool_called = expected_tools.issubset(actual_tools)
            tool_passed = correct_tool_called
        else:
            correct_tool_called = not tool_called
            tool_passed = not tool_called

        # -----------------------------
        # Response evaluation
        # -----------------------------
        response_passed = is_correct(
            expected=expected_output,
            actual=actual_output,
            tolerance=tolerance
        )

        # -----------------------------
        # Final row result
        # -----------------------------
        row_passed = tool_passed and response_passed

        if tool_passed:
            tool_correct += 1
        if response_passed:
            response_correct += 1

        results.append({
            "row_index": i,
            "prompt": prompt,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "expected_tools": list(expected_tools),
            "actual_tools": list(actual_tools),
            "tool_expected": tool_expected,
            "tool_called": tool_called,
            "correct_tool_called": correct_tool_called,
            "tool_passed": tool_passed,
            "response_passed": response_passed,
            "passed": row_passed
        })

        if verbose:
            print(f"--- ROW {i} ---")
            print("PROMPT              :", prompt)
            print("EXPECTED OUTPUT     :", expected_output)
            print("ACTUAL OUTPUT       :", actual_output)
            print("EXPECTED TOOLS      :", list(expected_tools))
            print("ACTUAL TOOLS        :", list(actual_tools))
            print("TOOL EXPECTED       :", tool_expected)
            print("TOOL CALLED         :", tool_called)
            print("CORRECT TOOL CALLED :", correct_tool_called)
            print("PASSED              :", row_passed)
            print()

    total = len(rows)

    tool_score = tool_correct / total
    response_score = response_correct / total

    final_score = (
        tool_score * tool_weight +
        response_score * response_weight
    )

    return round(final_score, 3), results
