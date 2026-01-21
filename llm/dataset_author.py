import json
import re
from typing import Optional

from llm.ollama_client import OllamaClient
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

# --------------------------------------------------
# Ollama client
# --------------------------------------------------
llm = OllamaClient(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL
)

MAX_ATTEMPTS = 3


# --------------------------------------------------
# JSON extraction helper
# --------------------------------------------------
def _extract_json(text: str) -> dict:
    """
    Extract the first JSON object from LLM output.
    Fails hard if no JSON is found.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(
            f"LLM output did not contain valid JSON:\n{text}"
        )
    return json.loads(match.group())


# --------------------------------------------------
# Dataset normalization (STRUCTURAL ONLY)
# --------------------------------------------------
def _normalize_dataset(dataset: dict) -> dict:
    """
    Enforce REQUIRED structure.
    Never invent or auto-fill ground truth.
    """
    if "rows" not in dataset or not isinstance(dataset["rows"], list):
        raise ValueError("Dataset missing 'rows' list")

    for i, row in enumerate(dataset["rows"]):
        if "input_prompt" not in row:
            raise ValueError(f"Row {i} missing input_prompt")

        if "expected_output" not in row:
            # 🚫 NEVER auto-fill gold answers
            raise ValueError(f"Row {i} missing expected_output")

        if "difficulty" not in row:
            raise ValueError(f"Row {i} missing difficulty")

        # Auto-fix expected_tools ONLY (safe)
        if "expected_tools" not in row or row["expected_tools"] is None:
            row["expected_tools"] = []

        if not isinstance(row["expected_tools"], list):
            raise ValueError(
                f"Row {i} expected_tools must be a list"
            )

    return dataset


# --------------------------------------------------
# Dataset writer (LLM + optional human guidance)
# --------------------------------------------------
def write_dataset(
    gravity,
    internet,
    domain,
    history,
    gan_plan,
    human_feedback: Optional[dict] = None
):
    """
    Generate a GOLD-STANDARD test dataset.

    Human feedback is OPTIONAL:
    - If provided and send_to_llm=true, it influences generation
    - Human overrides are applied OUTSIDE this file
    """

    # ----------------------------------------------
    # Optional human guidance to LLM
    # ----------------------------------------------
    human_prompt = ""
    if human_feedback and human_feedback.get("send_to_llm"):
        human_prompt = f"""
HUMAN DOMAIN EXPERT GUIDANCE (HIGH PRIORITY):
{json.dumps(human_feedback.get("llm_guidance", {}), indent=2)}
"""

    # ----------------------------------------------
    # Base prompt
    # ----------------------------------------------
    base_prompt = f"""
You are a senior QA engineer designing GOLD-STANDARD test datasets
for evaluating an AI agent.

Your task:
- Generate ONE dataset in VALID JSON
- The dataset must be realistic, precise, and human-like
- The dataset will be used for automated evaluation and deployment gating

CONTEXT
-------
Rules: {gravity}
Guidelines: {internet}
Agent Domain: {domain}
Previous datasets (do NOT duplicate): {history}
Edge-case plan (GAN-inspired): {gan_plan}

{human_prompt}

CRITICAL CONSTRAINTS
-------------------
1. Output ONLY valid JSON
2. Use EXACTLY 10 rows
3. Every row MUST include:
   - input_prompt
   - expected_output
   - expected_tools
   - difficulty
4. expected_output is REQUIRED and must NEVER be omitted
5. expected_tools must be [] if no tool is required
6. Do NOT invent field names
7. No markdown, no comments, no explanations

SYMBOLIC POLICY:
- Do NOT create prompts that require symbolic outputs unless domain.capabilities includes "symbolic_math".
- If a prompt has multiple variables without numeric values, expected_output MUST be an error like:
  "Error: insufficient information"

DATASET FORMAT
--------------
{{
  "dataset_name": string,
  "intent": string,
  "agent_type": string,
  "rows": [
    {{
      "input_prompt": string,
      "expected_output": string,
      "expected_tools": [string],
      "difficulty": "easy" | "medium" | "hard"
    }}
  ],
  "evaluation_rules": {{
    "min_score": number,
    "tool_accuracy_weight": number,
    "response_accuracy_weight": number
  }}
}}
"""

    last_error = None

    # ----------------------------------------------
    # Retry loop (STRICT)
    # ----------------------------------------------
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = llm.generate(base_prompt)

            dataset = _extract_json(response)
            dataset = _normalize_dataset(dataset)

            return dataset

        except ValueError as e:
            last_error = e
            print(
                f"Dataset generation attempt {attempt} failed: {e}"
            )

    # ----------------------------------------------
    # Hard fail after retries
    # ----------------------------------------------
    raise RuntimeError(
        f"Failed to generate valid dataset after {MAX_ATTEMPTS} attempts.\n"
        f"Last error: {last_error}"
    )
