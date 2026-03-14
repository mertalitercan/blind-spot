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
    import re
    text = text.strip()

    # Try to extract JSON from markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Direct parse
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Try to find JSON object anywhere in the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    return {}
