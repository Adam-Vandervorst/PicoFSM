from typing import TypeVar
from functools import partial


base_state = TypeVar('B')


def fsm_of(base_class):
    # __new__ replacement
    def _new(fsmcls, _, *a, **kw):
        # map states to list of transitions
        fsmcls.__map = {base_state: []}

        for name, val in fsmcls.__dict__.items():
            if isinstance(val, TypeVar):
                fsmcls.__map[val] = []
            elif callable(val) and hasattr(val, 'start'):
                fsmcls.__map[val.start].append((val, val.end))

        fsmcls.__cur = base_state

        # make actual new classes
        bc = _old(base_class)
        bc.fsm = fsmcls()
        return bc

    # __setattr__ replacement
    def _setattr(ins, name, value):
        # set the actual value
        super(base_class, ins).__setattr__(name, value)

        # gather context for checks
        context = base_class.__dict__.copy()
        context.update(ins.__dict__)

        # loop over transitions from this state
        for func, ret in ins.fsm.__map[ins.fsm.__cur]:
            if name in func.names and func.cond(context):
                func(ins)  # execute transition
                if ret is not ...:  # change state
                    ins.fsm.__cur = ret

    def wrapper(fsmcls):
        base_class.__new__ = partial(base_class.__new__, fsmcls)
        return fsmcls

    _old = base_class.__new__
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
