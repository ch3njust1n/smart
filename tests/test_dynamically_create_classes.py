import textwrap
from pprint import pprint

def test_generated_class():
    def my_func(self):
        return self.x * 2

    MyClass = type('MyClass', (object,), {'x': 10, 'my_func': my_func})
    instance = MyClass()
    assert instance.x == 10
    assert instance.my_func() == 20


def test_generated_stringified_class():
    properties = textwrap.dedent("""
    {
        'x': 10, 
        'my_func': 
            '''def my_func(self):
                return self.x * 2
            '''
    }
    """)
    properties = eval(properties)
    pprint(properties)
    global_vars = {}
    func_source = properties['my_func']
    exec(func_source, global_vars)
    properties['my_func'] = global_vars['my_func']

    MyClass = type('MyClass', (object,), properties)
    instance = MyClass()

    assert instance.x == 10
    assert instance.my_func() == 20