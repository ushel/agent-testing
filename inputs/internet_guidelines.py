INTERNET_GUIDELINES = """
Sourced from:
- OpenAI Evals documentation
- Google LLM evaluation best practices
- RAGAS evaluation framework
- Industry QA testing blogs

Best practices:
- Test both happy paths and failure modes
- Include malformed and ambiguous inputs
- Prefer fewer high-quality test cases over many shallow ones
- Always include ground-truth expected outputs
- Separate dataset generation from evaluation logic
- Avoid data leakage from training data
- Include adversarial and red-team style prompts
- Ensure numeric tolerance for approximate answers
"""
