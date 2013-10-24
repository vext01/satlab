class Node(object):
    pass

class Lit(Node):

    def __init__(self, name):
        self.name = name # symbolic name
        self.children = [] # terminal

    def __str__(self): return self.name

class BinaryNode(Node):

    def __init__(self, oper_str, left, right):
        self.oper_str = oper_str
        self.children = [left, right]

    def __str__(self):
        return "%s %s %s" % (self.children[0], self.oper_str, self.children[1])

class And(BinaryNode):

    def __init__(self, left, right):
        super(And, self).__init__(".", left, right)

class Or(BinaryNode):

    def __init__(self, left, right):
        super(Or, self).__init__("+", left, right)


# XXX just a test
if __name__ == "__main__":
    (a, b, c) = (Lit("a"), Lit("b"), Lit("c"))

    a = And(a, Or(b, c))
