import pytest
from model import gpt, claude
from utils import extract_func_name
from meta import generate_attribute


@pytest.fixture
def model_resp():
    return {
        "actions": [
            {
                "component": "device",
                "action": "save-custom-mode",
                "parameters": "study-mode",
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


def test_imagined_action_with_gpt():
    @generate_attribute(model=gpt)
    class Mobile(object):
        def __init__(self):
            pass

        def phone(self):
            pass

        def wifi(self):
            pass

    mobile = Mobile()
    results = []

    for action in model_resp["actions"]:
        func_name = action["action"]
        try:
            results.append(getattr(mobile, func_name)())
        except AttributeError:
            func_src = gpt(str(action))
            global_vars = {}
            exec(func_src, global_vars)
            func_name = extract_func_name(func_src)
            generated_func = global_vars[func_name]
            results.append(generated_func())
