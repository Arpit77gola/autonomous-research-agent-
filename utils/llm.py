import os
from functools import lru_cache
from langchain_groq import ChatGroq


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.3) -> ChatGroq:
    """Return a cached ChatGroq instance."""
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set")
    return ChatGroq(
        api_key=api_key,
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=temperature,
        max_tokens=4096,
    )