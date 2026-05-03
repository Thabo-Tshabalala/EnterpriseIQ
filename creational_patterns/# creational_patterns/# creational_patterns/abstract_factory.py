# creational_patterns/abstract_factory.py
# Pattern: Abstract Factory
# Use Case: LLM provider families — OpenAI vs Ollama (local).
# Justification: EnterpriseIQ supports two LLM deployment modes:
# cloud (OpenAI API) and air-gapped (local Ollama). Each mode requires
# a matching EmbeddingService and LLMClient that work together as a family.
# The Abstract Factory ensures the correct pair is always created together,
# preventing a mismatch like using OpenAI embeddings with an Ollama LLM.

from abc import ABC, abstractmethod


# ─── Abstract Products ───────────────────────────────────────────

class EmbeddingService(ABC):
    """Abstract embedding service — converts text to vectors."""

    @abstractmethod
    def embed(self, text: str) -> list:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


class LLMClient(ABC):
    """Abstract LLM client — generates responses from prompts."""

    @abstractmethod
    def call_api(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


# ─── Concrete Products: OpenAI Family ────────────────────────────

class OpenAIEmbeddingService(EmbeddingService):
    def embed(self, text: str) -> list:
        # Stub: production calls OpenAI text-embedding-3-small
        print(f"[OpenAI Embedding] Embedding text via OpenAI API")
        return [0.1] * 1536  # OpenAI ada-002 dimension

    def get_model_name(self) -> str:
        return "text-embedding-3-small"


class OpenAILLMClient(LLMClient):
    def call_api(self, prompt: str) -> str:
        # Stub: production calls gpt-4o via OpenAI API
        print(f"[OpenAI LLM] Calling GPT-4o")
        return "OpenAI GPT-4o stub response."

    def get_model_name(self) -> str:
        return "gpt-4o"


# ─── Concrete Products: Ollama (Local) Family ─────────────────────

class OllamaEmbeddingService(EmbeddingService):
    def embed(self, text: str) -> list:
        # Stub: production calls local Ollama nomic-embed-text
        print(f"[Ollama Embedding] Embedding text via local Ollama")
        return [0.1] * 768  # nomic-embed-text dimension

    def get_model_name(self) -> str:
        return "nomic-embed-text"


class OllamaLLMClient(LLMClient):
    def call_api(self, prompt: str) -> str:
        # Stub: production calls local Ollama llama3
        print(f"[Ollama LLM] Calling local llama3")
        return "Ollama llama3 stub response."

    def get_model_name(self) -> str:
        return "llama3"


# ─── Abstract Factory ─────────────────────────────────────────────

class LLMProviderFactory(ABC):
    """Abstract factory — creates a matching pair of embedding service and LLM client."""

    @abstractmethod
    def create_embedding_service(self) -> EmbeddingService:
        pass

    @abstractmethod
    def create_llm_client(self) -> LLMClient:
        pass


# ─── Concrete Factories ───────────────────────────────────────────

class OpenAIProviderFactory(LLMProviderFactory):
    """Creates the OpenAI family: OpenAI embeddings + OpenAI LLM."""

    def create_embedding_service(self) -> EmbeddingService:
        return OpenAIEmbeddingService()

    def create_llm_client(self) -> LLMClient:
        return OpenAILLMClient()


class OllamaProviderFactory(LLMProviderFactory):
    """Creates the Ollama family: Ollama embeddings + Ollama LLM."""

    def create_embedding_service(self) -> EmbeddingService:
        return OllamaEmbeddingService()

    def create_llm_client(self) -> LLMClient:
        return OllamaLLMClient()


def get_provider_factory(provider: str) -> LLMProviderFactory:
    """Helper — returns the correct factory based on configuration."""
    if provider.lower() == "openai":
        return OpenAIProviderFactory()
    elif provider.lower() == "ollama":
        return OllamaProviderFactory()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
