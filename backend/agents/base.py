"""Shared Railtracks agent configuration and LLM instance."""

import json
import railtracks as rt
from config import settings


def get_llm():
    """Create the shared Anthropic LLM instance for all agents."""
    return rt.llm.AnthropicLLM(
        settings.MODEL_NAME,
        api_key=settings.ANTHROPIC_API_KEY,
    )


def parse_agent_json(text: str) -> dict:
    """Extract JSON from agent response text, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}
