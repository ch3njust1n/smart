import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock
from .model import GPT4, Claude
from generative.classes import generate_attribute


@pytest.fixture
def model_resp():
    return {
        "actions": [
            {
                "component": "device",
                "action": "save-custom-mode",
                "parameter": "study-mode",
                "commands": [
                    {
                        "component": "app",
                        "action": "disable-notifications",
                        "parameters": "",
                    },
                    {
                        "component": "device",
                        "action": "set-volume",
                        "parameters": "0",
                    },
                    {"component": "call", "action": "block-all", "parameters": ""},
                    {"component": "text", "action": "block-all", "parameters": ""},
                    {
                        "component": "call",
                        "action": "unblock",
                        "parameters": "555-555-5555",
                    },
                    {
                        "component": "text",
                        "action": "unblock",
                        "parameters": "555-555-5555",
                    },
                ],
            }
        ]
    }


@pytest.fixture
def mock_gpt4_generate_attributes():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
    def save_custom_mode(modes):
        for mode in modes['study-mode']:
            if mode['action'] == 'disable-notifications':
                disable_notifications(mode['component'])
            elif mode['action'] == 'set-volume':
                set_volume(mode['component'], mode['parameters'])
            elif mode['action'] in ['block-all', 'unblock']:
                manage_block(mode['component'], mode['action'], mode['parameters'])
    """
    return response


@pytest.mark.parametrize("model,critic", [(GPT4, Claude)])
def test_imagined_action_with_gpt(
    model, critic, model_resp, mock_gpt4_generate_attributes
):
    mock_anthropic = MagicMock()

    with mock.patch(
        "openai.ChatCompletion.create", return_value=mock_gpt4_generate_attributes
    ):
        with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
            with mock.patch.object(critic, "generate", return_value="True"):

                @generate_attribute(model=model, critic=critic)
                class Mobile(object):
                    def __init__(self):
                        pass

                    def phone(self):
                        pass

                    def wifi(self):
                        pass

                mobile = Mobile()

                for action in model_resp["actions"]:
                    func_name = action["action"]
                    kwarg = {action["parameter"]: str(action["commands"])}
                    try:
                        res = getattr(mobile, func_name)(**kwarg)
                        assert res != None
                        break
                    except AttributeError:
                        assert False
