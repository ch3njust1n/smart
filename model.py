"""
User-defined functions that generate code using LLM.
"""

import os
import openai
from dotenv import load_dotenv

load_dotenv()

"""
OpenAI Completion API wrapper

Args:
    prompt (string): The source code as context for function to replace.

Returns:
    Source code of the generated function.
"""


def llm(prompt: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if openai.api_key is None:
        raise ValueError(
            "The OPENAI_API_KEY environment variable is not set. Please provide your OpenAI API key."
        )

    llm_code = openai.Completion.create(
        model=os.getenv("MODEL"),
        prompt=prompt,
        temperature=float(os.getenv("TEMPERATURE", 0.7)),
        max_tokens=int(os.getenv("MAX_TOKENS", 3600)),
    )

    return llm_code.choices[0].text
