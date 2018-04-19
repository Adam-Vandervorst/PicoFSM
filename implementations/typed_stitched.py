from typing import TypeVar
from functools import partial

base_state = TypeVar('B')


def fsm_of(base_class):
    def create(cls, ins):
        def __next__(self):
            to_check = dict(cls.__dict__)
            to_check.update(ins.__dict__)
            for func, ret in self.__map[self.__cur]:
                if func.cond(to_check):
                    func(self)
                    self.__cur = self.__cur if ret is ... else ret
        return __next__

    def new(fsmcls, _, *args, **kwargs):
        fsm = type('FSM', (fsmcls,), {'__map': {base_state: []},
                                      '__cur': base_state})

        for name, val in fsmcls.__dict__.items():
            if callable(val):
                if isinstance(val, TypeVar):
                    fsm.__map[val] = []
                elif hasattr(val, 'start'):
                    fsm.__map[val.start].append((val, val.end))

        bc = object.__new__(base_class)
        fsm.__next__ = create(base_class, bc)
        fsmi = object.__new__(fsm)
        bc.fsm = fsmi
        return bc

    def wrapper(cls):
        base_class.__new__ = partial(base_class.__new__, cls)
        return cls

    base_class.__new__ = new
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
