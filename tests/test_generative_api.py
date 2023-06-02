import time
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


def test_imagined_action_with_gpt(model_resp):
    @generate_attribute(model=claude)
    class Mobile(object):
        def __init__(self):
            pass

        def phone(self):
            pass

        def wifi(self):
            pass

    mobile = Mobile()
    results = []

    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:
            for action in model_resp["actions"]:
                func_name = action["action"]
                kwarg = {
                    action['parameter']: str(action['commands'])
                }
                try:
                    # Change this line
                    res = getattr(mobile, func_name)(**kwarg)
                    print(res)
                    assert res != None
                    break
                except AttributeError:
                    raise Exception("@generate_attribute decorator failed to generate function")
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)
