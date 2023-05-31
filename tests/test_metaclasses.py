import sys
from metaclasses.demo import Car, GenerativeMetaClass
from io import StringIO


def test_traditional_metaclass():
    honk_code = """
def honk(self, times=1):
    for i in range(times):
        print(f'{i} - Beep beep!')
"""
    GenerativeMetaClass.generate(Car, honk_code)
    my_car = Car()
    backup = sys.stdout  # Backup original standard output
    sys.stdout = StringIO()  # Redirect standard output
    my_car.honk(3)
    output = sys.stdout.getvalue()  # Get redirected output
    sys.stdout.close()
    sys.stdout = backup  # Restore original standard output
    assert output == "0 - Beep beep!\n1 - Beep beep!\n2 - Beep beep!\n"
