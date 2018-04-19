from implementations.typed_fsmdecorator import fsm_of, base_state, on, TypeVar


class A:
    test = False

    def __init__(self, i):
        self.i = i


# noinspection PyTypeChecker
@fsm_of(A)
class Simple:
    exited = TypeVar('E')

    @on('not test')
    def trans1(fsm: base_state) -> ...:
        print('trans1 going')

    @on('test')
    def trans2(fsm: base_state) -> exited:
        print('trans2 going')

    @on('abs(i) >= 10')
    @on('i == 2')
    def transb(fsm: exited) -> base_state:
        print('transb going')


t = Simple(2)
next(t)
t.test = True
next(t)
next(t)
next(t)
t.i = 8
next(t)
t.i = 15
next(t)
