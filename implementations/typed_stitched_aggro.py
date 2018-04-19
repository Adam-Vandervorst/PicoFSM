from typing import TypeVar
from functools import partial

base_state = TypeVar('B')


def fsm_of(base_class):
    def _new(fsmcls, _, *a, **kw):
        fsmcls.__map = {base_state: []}

        for name, val in fsmcls.__dict__.items():
            if callable(val):
                if isinstance(val, TypeVar):
                    fsmcls.__map[val] = []
                elif hasattr(val, 'start'):
                    fsmcls.__map[val.start].append((val, val.end))

        fsmcls.__cur = base_state

        bc = object.__new__(base_class)
        fsmi = object.__new__(fsmcls)
        bc.fsm = fsmi
        return bc

    def _setattr(ins, name, value):
        super(base_class, ins).__setattr__(name, value)

        to_check = dict(base_class.__dict__)
        to_check.update(ins.__dict__)

        for func, ret in ins.fsm.__map[ins.fsm.__cur]:
            if name in func.names:
                if func.cond(to_check):
                    func(ins)
                    if ret is not ...:
                        ins.fsm.__cur = ret

    def wrapper(fsmcls):
        base_class.__new__ = partial(base_class.__new__, fsmcls)
        return fsmcls

    base_class.__new__ = _new
    base_class.__setattr__ = _setattr
    return wrapper


def on(cond):
    cond_code = compile(cond, '<dis>', 'eval')

    def wrapper(trans):
        if hasattr(trans, 'start'):  # chained wrapper
            prev_cond = trans.cond
            trans.cond = lambda ctx: eval(cond_code, {}, ctx) or prev_cond(ctx)
            trans.names.update(cond_code.co_names)
        else:
            trans.start = trans.__annotations__[trans.__code__.co_varnames[0]]
            trans.end = trans.__annotations__['return']
            trans.cond = lambda ctx: eval(cond_code, {}, ctx)
            trans.names = set(cond_code.co_names)
        return trans
    return wrapper
