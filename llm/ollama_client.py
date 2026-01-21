import requests

class OllamaClient:
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
        }

        r = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=300,
        )

        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
