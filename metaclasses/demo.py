from meta import GenerativeMetaClass


class Car(metaclass=GenerativeMetaClass):
    def __init__(self):
        pass


class Doggo(metaclass=GenerativeMetaClass):
    def __init__(self, name: str):
        self.name = name

    def set_treat(self, treat: str):
        self.stomach = treat
