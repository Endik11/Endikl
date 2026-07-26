class ActionNode:
    def __init__(self, action): self.action = action
    def evaluate(self, context): return self.action(context)


class SelectorNode:
    def __init__(self, *children): self.children = children
    def evaluate(self, context):
        for child in self.children:
            result = child.evaluate(context)
            if result is not None: return result
        return None
