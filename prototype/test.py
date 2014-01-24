import inspect


class A(object):
    def f(self, x):
        print('hello {}'.format(x))


def g(b=False, *args, **kwargs):
    print('world {}'.format(b))


def h():
    print('today')


class B(object):
    def __init__(self, func):
        print('ismethod {}'.format(inspect.ismethod(func)))
        print('isfunction {}'.format(inspect.isfunction(func)))
        print('isroutine {}'.format(inspect.isroutine(func)))
        print('getargspec {}'.format(inspect.getargspec(func)))
        self.func = func

    def handle(self, *args, **kwargs):
        self.func(*args, **kwargs)

a = A()

b = B(a.f)
#b.handle()
b.handle(50)
b.handle('some_text')
b.handle(True)

b = B(g)
b.handle()
b.handle(50)
b.handle('some_text')
b.handle(True)

b = B(h)
b.handle()
#b.handle(50)
#b.handle('some_text')
#b.handle(True)

#assert inspect.isroutine(a), 'gaegaegae'


def func(a, b, c=False, d='stat'):
    print(a, b, c, d)

print('ismethod {}'.format(inspect.ismethod(func)))
print('isfunction {}'.format(inspect.isfunction(func)))
print('isroutine {}'.format(inspect.isroutine(func)))
print('getargspec {}'.format(inspect.getargspec(func)))

d = {'a': 5}
c = d.copy()
c['a'] = 6

print(d)
print(c)

call_args = {
    'a': 'hello',
    'b': 'world',
    'c': True,
    'd': '!'
}
func(**call_args)

print(RuntimeError('afeafae'))
