class Phase:
    def __init__(self, name, execute_fn):
        self.name = name
        self.execute_fn = execute_fn

    def execute(self):
        self.execute_fn()
