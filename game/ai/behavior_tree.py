class BehaviorTree:
    def __init__(self, root): self.root = root
    def evaluate(self, context): return self.root.evaluate(context)
