import httpx


class VeniceClient:
    def __init__(self, api_key: str):
        self.api_key: str = api_key
        self.base_url: str = "https://api.venice.ai/api/v1"
        self.timeout: float = 60.0

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def embed(self, text: list[str], dimensions: int = 300) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"
        payload = {
            "encoding_format": "float",
            "input": text,
            "model": "text-embedding-bge-m3",
            "dimensions": dimensions,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            embeddings = data["data"]
            embeddings.sort(key=lambda x: x["index"])
            return [embedding["embedding"] for embedding in embeddings]
    
    async def chat_complete(self, payload: dict) -> str:
        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            try:
                return data["choices"][0]["message"]["content"]
            except (IndexError, KeyError):
                raise ValueError(f"Unexpected VeniceAI API response format: {data}")