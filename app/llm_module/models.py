from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class LLM:
    name: str
    provider: str
    model: str
    fallback_to: Optional[str] = None

AVAILABLE_LLMS: Dict[str, LLM] = {
    "gemini-2.5-flash": LLM(name="gemini-2.5-flash", provider="google", model="gemini-2.5-flash", fallback_to="gemini-1.5-flash"),
    "gemini-1.5-flash": LLM(name="gemini-1.5-flash", provider="google", model="gemini-1.5-flash", fallback_to="mistral-small-2503"),
    "mistral-small-2503":LLM(name="mistral-small-2503",provider="mistral",model="mistral-small-2503", fallback_to=None),
    "gpt-40-mini": LLM(name="gpt-40-mini", provider="openai", model="gpt-40-mini", fallback_to=None)
}
