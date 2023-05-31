import sys
from metaclasses.demo import Car
from io import StringIO


def test_traditional_metaclass():
    my_car = Car()
    backup = sys.stdout  # Backup original standard output
    sys.stdout = StringIO()  # Redirect standard output
    my_car.honk(3)
    output = sys.stdout.getvalue()  # Get redirected output
    sys.stdout.close()
    sys.stdout = backup  # Restore original standard output
    assert output == "0 - Beep beep!\n1 - Beep beep!\n2 - Beep beep!\n"
