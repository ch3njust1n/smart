class MetaCar(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        honk_code = """
def honk(self, times=1):
    for i in range(times):
        print(f'{i} - Beep beep!')
"""
        local_dict = {}
        exec(honk_code, {}, local_dict)
        setattr(cls, "honk", local_dict["honk"])


class Car(metaclass=MetaCar):
    def __init__(self):
        pass
