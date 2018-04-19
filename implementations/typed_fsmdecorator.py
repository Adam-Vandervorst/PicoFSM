from typing import TypeVar

base_state = TypeVar('B')


def fsm_of(base_class):
    def __next__(self):
        for func, ret in self.__map[self.__cur]:
            if func.cond({**base_class.__dict__, **self.__dict__}):
                func(self)
                self.__cur = self.__cur if ret is ... else ret

    def __new__(cls, *args, **kwargs):
        cls.__map = {base_state: []}

        for name, val in cls.__dict__.copy().items():
            if callable(val):
                if isinstance(val, TypeVar):
                    cls.__map[val] = []
                elif hasattr(val, 'start'):
                    cls.__map[val.start].append((val, val.end))

        cls.__cur = base_state

        i = type(cls.__name__, (base_class, cls), {'__next__': __next__})
        base_class.__init__(i, *args, **kwargs)
        return object.__new__(i)

    def wrapper(cls):
        cls.__new__ = __new__
        return cls
    return wrapper


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
