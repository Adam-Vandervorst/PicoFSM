from lib.fsmsuper import FSM


class Simple(FSM):
    test = False

    def __init__(self, i):
        self.i = i

    def Base(self):
        if self.test:
            print('trans2 going')
            return self.Exited
        else:
            print('trans1 going')

    def Exited(self):
        if abs(self.i) >= 10 or self.i == 2:
            print('transb going')
            return self.Base

    state = Base


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
