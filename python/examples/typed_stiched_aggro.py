from lib.typed_stitched_aggro import fsm_of, base_state, on, TypeVar


class Abase():
    test = False


class A(Abase):
    def __init__(self, i):
        self.i = i


# noinspection PyTypeChecker
@fsm_of(A)
class Simple:
    exited = TypeVar('E')

    @on('not test')
    def trans1(fsm: base_state) -> ...:
        print("Not testing anymore")

    @on('test')
    def get_exited(fsm: base_state) -> exited:
        print("Preparing the test")

    @on('abs(i) >= 10')
    @on('i == 2')
    def fall_back(fsm: exited) -> base_state:
        print(f"Do the test with i={fsm.i}")


a = A(2)
a.test = True
a.i = 8
a.i = 15
a.test = False
