from typing import List
from .models import AVAILABLE_LLMS
from .client_manager import LLMClientManager
import logging

logger = logging.getLogger(__name__)


class LLMCaller:
    def __init__(self, client_manager: LLMClientManager):
        self.client_manager = client_manager

    def _get_fallback_chain(self, llm_name: str) -> List[str]:
        chain = []
        current = llm_name
        while current:
            chain.append(current)
            llm = AVAILABLE_LLMS.get(current)
            if llm is None:
                break
            current = llm.fallback_to
        return chain

    def llm_call(self, llm_name: str, messages: List[dict]):
        chain = self._get_fallback_chain(llm_name)
        last_exception = None

        for name in chain:
            client = self.client_manager.get_client(name)
            if client is None:
                logger.warning(f"Client for LLM '{name}' not found, skipping.")
                continue

            try:
                logger.info(f"Calling LLM '{name}'")
                response = client.chat.completions.create(
                    model=AVAILABLE_LLMS[name].model,
                    messages=messages,
                )
                return response
            except Exception as e:
                logger.warning(f"LLM '{name}' call failed: {e}")
                last_exception = e

        raise Exception(
            f"All LLM calls failed in fallback chain {chain}") from last_exception
