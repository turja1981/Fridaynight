from __future__ import annotations
from langchain_core.language_models import BaseChatModel


def create_llm(
    provider: str,
    model: str,
    api_key: str = "",
    max_tokens: int = 1024,
    streaming: bool = False,
    **kwargs,
) -> BaseChatModel:
    """Return a LangChain chat model for the requested provider.

    Supported providers: ``anthropic`` (default), ``openai``, ``google``.
    Raises ImportError if the matching langchain package is not installed.
    """
    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ImportError(
                "Install langchain-openai to use the OpenAI provider: "
                "pip install langchain-openai"
            ) from exc
        return ChatOpenAI(
            model=model,
            api_key=api_key or None,
            max_tokens=max_tokens,
            streaming=streaming,
            **kwargs,
        )

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:
            raise ImportError(
                "Install langchain-google-genai to use the Google provider: "
                "pip install langchain-google-genai"
            ) from exc
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key or None,
            max_output_tokens=max_tokens,
            streaming=streaming,
            **kwargs,
        )

    # Default: Anthropic / Claude
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(
        model=model,
        api_key=api_key or None,
        max_tokens=max_tokens,
        streaming=streaming,
        **kwargs,
    )
