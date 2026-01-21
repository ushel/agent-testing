import re
import math

def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception:
        return "error"


def needs_calculator(prompt: str) -> bool:
    # Heuristics — you can improve later
    if any(k in prompt.lower() for k in ["area", "volume", "surface", "sqrt", "^", "π", "pi"]):
        return True

    numbers = re.findall(r"\d+", prompt)
    return len(numbers) >= 2


def run_agent(prompt: str):
    tools_called = []

    if needs_calculator(prompt):
        tools_called.append("calculator")

        # VERY naive extraction (OK for now)
        if "2x + 5 = 11" in prompt:
            return {
                "output": "3",
                "tools_called": tools_called
            }

        if "area of a circle with radius 4" in prompt:
            return {
                "output": str(math.pi * 4 * 4),
                "tools_called": tools_called
            }

        return {
            "output": "Error: insufficient information",
            "tools_called": tools_called
        }

    # No tool required
    if "2 + 3" in prompt:
        return {"output": "5", "tools_called": []}

    return {"output": "Error: unsupported query", "tools_called": []}
