import os
from openai import OpenAI
from langsmith.wrappers import wrap_openai
from typing import Dict
from .models import AVAILABLE_LLMS, LLM
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class LLMClientManager:
    def __init__(self):
        self.clients: Dict[str, OpenAI] = {}
        self._create_clients()

    def _create_clients(self):
        for llm_name, llm in AVAILABLE_LLMS.items():
            if llm.provider == "google":
                base_url = "https://generativelanguage.googleapis.com/v1beta/"
                api_key = os.getenv("GOOGLE_API_KEY")
            elif llm.provider == "openai":
                base_url = "https://api.openai.com/v1"
                api_key = os.getenv("OPENAI_API_KEY")
            elif llm.provider == "mistral":
                base_url = "https://api.mistral.ai/v1/"
                api_key = os.environ.get("MISTRAL_API_KEY")
            else:
                logger.warning(
                    f"Unknown provider {llm.provider} for LLM {llm_name}, skipping client creation.")
                continue

            if not api_key:
                logger.warning(
                    f"API key not found for provider {llm.provider}. Client not created.")
                continue

            client = OpenAI(api_key=api_key, base_url=base_url)
            wrapped_client = wrap_openai(client)
            self.clients[llm_name] = wrapped_client

    def get_client(self, llm_name: str) -> OpenAI:
        return self.clients.get(llm_name)
