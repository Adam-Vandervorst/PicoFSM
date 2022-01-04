class FSM:
    def __next__(self):
        new, old = self.state(), self.state
        self.state = new if new else old
