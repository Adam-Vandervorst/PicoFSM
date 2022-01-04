from typing import TypeVar


class FSM:
    base = TypeVar('B')

    __cur = base
    __map = {base: []}

    def __next__(self):
        for func, ret in self.__map[self.__cur]:
            if func.cond(self.__dict__):
                func(self)
                self.__cur = self.__cur if ret is ... else ret

    def __new__(cls, *args, **kwargs):
        for val in vars(cls).values():
            if isinstance(val, TypeVar):
                cls.__map[val] = []

        for val in vars(cls).values():
            if callable(val) and hasattr(val, 'start'):
                cls.__map[val.start].append((val, val.end))
        return object.__new__(cls)

    @staticmethod
    def on(cond):
        def wrapper(trans):
            if hasattr(trans, 'start'):  # chained wrapper
                prev_cond = trans.cond
                trans.cond = lambda ctx: eval(cond, {}, ctx) or prev_cond(ctx)
            else:
                trans.start = trans.__annotations__[trans.__code__.co_varnames[0]]
                trans.end = trans.__annotations__['return']
                trans.cond = lambda ctx: eval(cond, {}, ctx)
            return trans
        return wrapper
