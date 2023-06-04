import pytest
from model import gpt4
from generative.decorators import generate_attribute


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


@pytest.mark.skip(reason="For illustration purposes only")
def test_imagined_action_with_gpt(model_resp):
    @generate_attribute(model=gpt4)
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
