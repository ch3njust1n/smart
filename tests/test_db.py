import json
import redis
import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock, patch
from typing import Any, Dict, List

from generative.functions import adapt
from generative.metaclasses import AbstractDatabase
from .model import GPT4, Claude


class VectorDB(AbstractDatabase):
    def __init__(self):
        self.db = redis.Redis(host="localhost", port=6379, db=0)

    def contains(self, key: str) -> bool:
        return bool(self.db.exists(key))

    def get(self, query: str) -> List[Dict]:
        result = self.db.get(query)

        if result is None:
            return []
        else:
            return json.loads(result.decode("utf-8"))

    def set(self, data: Any) -> None:
        key: str = data["function_name"]
        self.db.set(key, data)


@pytest.fixture
def mock_gpt4_selfheal():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
        def fibonacci(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fibonacci(n-1) + fibonacci(n-2)
    """
    return response


@pytest.fixture
def mock_anthropic_check_true():
    response = MagicMock()
    response.__getitem__.return_value = "True"
    return response


@pytest.fixture
def mock_vector_db():
    mock_db = VectorDB()
    mock_db.contains = MagicMock(return_value=True)
    mock_db.get = MagicMock(
        return_value="""
        def fibonacci(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fibonacci(n-1) + fibonacci(n-2)
    """
    )
    mock_db.set = MagicMock()
    return mock_db


@pytest.mark.parametrize("model,critic", [(GPT4, Claude)])
def test_selfheal_with_gpt4(
    model, critic, mock_gpt4_selfheal, mock_anthropic_check_true, mock_vector_db
):
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_true

    with patch("openai.ChatCompletion.create", return_value=mock_gpt4_selfheal):
        with patch("anthropic.Anthropic", return_value=mock_anthropic):
            with mock.patch.object(critic, "generate", return_value="True"):

                @adapt(model=model, critic=critic, database=mock_vector_db)
                def fibonacci(n):
                    if n <= 0:
                        return 0
                    elif n == 1:
                        return 1
                    else:
                        return fibonacci(n - 1) + fibonacci(n - 2) + 1

                assert fibonacci(8) == 21

                # Now, we'll assert that the mock Redis was interacted with as expected.
                mock_vector_db.contains.assert_called_once()
                mock_vector_db.set.assert_called_once()
