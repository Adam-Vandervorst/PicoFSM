from lib.typed_fsmsuper import FSM, TypeVar


# noinspection PyTypeChecker
class Simple(FSM):
    exited = TypeVar('E')

    def __init__(self, i):
        self.i = i

    @FSM.on('not test')
    def trans1(fsm: FSM.base) -> ...:
        print('trans1 going')

    @FSM.on('test')
    def trans2(fsm: FSM.base) -> exited:
        print('trans2 going')

    @FSM.on('abs(i) >= 10')
    @FSM.on('i == 2')
    def transb(fsm: exited) -> FSM.base:
        print('transb going')


t = Simple(2)
t.test = False
next(t)
t.test = True
next(t)
next(t)
next(t)
t.i = 8
next(t)
t.i = 15
next(t)
