class Node(object):

    def __init__(self): self.in_cnf = False

    # top level CNF conversion
    def to_cnf(self):
        tree = self._to_cnf(Lit.new_internal())
        tree.in_cnf = True
        return tree

    def is_cnf(self): return self.in_cnf
    def _to_cnf(self): raise RuntimeError("not implemented in base class")
    def is_leaf(self): raise RuntimeError("not implemented in base class")

class UnaryNode(Node):
    def __init__(self, oper_str, arg):
        self.oper_str = oper_str
        self.children = [ arg ]
        super(UnaryNode, self).__init__()

    def __str__(self): return "%s%s" % (self.oper_str, self.children[0])
    def is_leaf(self): return False

class Not(UnaryNode):
    def __init__(self, arg):
        super(Not, self).__init__("~", arg)

class Lit(Node):

    SERIAL = 0 # number used for generating variable names

    def __init__(self, name, internal=False):
        if not internal and name[0] == "_":
            raise RuntimeError(
                "User variables cannot start with underscore: '%s'" % name)
        self.name = name # symbolic name
        self.children = [] # terminal

    def _to_cnf(self, witness):
        # witness <=> self
        # is equiv to:
        # witness => self AND self => witness
        # which is equiv to:
        # (NOT witness OR self) AND (NOT self OR witness)
        #c1 = Or(Not(witness), self)
        #c2 = Or(self, Not(witness))
        #return And(c1, c2)

        # A literal is already CNF
        return self

    def __str__(self): return self.name
    def is_leaf(self): return True

    @staticmethod
    def new_internal():
        l = Lit("_x%d" % Lit.SERIAL, True)
        Lit.SERIAL += 1
        return l

class BinaryNode(Node):

    def __init__(self, oper_str, left, right):
        self.oper_str = oper_str
        self.children = [left, right]

    def __str__(self):
        return "%s %s %s" % (self.children[0], self.oper_str, self.children[1])

    def is_leaf(self): return False

class And(BinaryNode):

    def __init__(self, left, right):
        super(And, self).__init__(".", left, right)

    def _to_cnf(self, witness):
        # W <=> L.R   becomes   (L+~W).(R+~W).(~L+~R+W)
        new_witness = Lit.new_internal()

        left_cnf = self.children[0]._to_cnf(new_witness)
        right_cnf = self.children[1]._to_cnf(new_witness)

        c1 = Or(left_cnf, Not(witness))
        c2 = Or(right_cnf, Not(witness))
        c3 = Or(Not(left_cnf), Or(Not(right_cnf), witness))

        return And(c1, And(c2, c3))

class Or(BinaryNode):

    def __init__(self, left, right):
        super(Or, self).__init__("+", left, right)

    def _to_cnf(self, witness):
        # W <=> L+R   becomes   (~L+W).(~R+W).(L+R+~W)
        new_witness = Lit.new_internal()

        left_cnf = self.children[0]._to_cnf(new_witness)
        right_cnf = self.children[1]._to_cnf(new_witness)

        c1 = Or(Not(left_cnf), witness)
        c2 = Or(Not(right_cnf), witness)
        c3 = Or(left_cnf, Or(right_cnf, Not(witness)))

        return And(c1, And(c2, c3))

# XXX just a test
if __name__ == "__main__":
    (a, b, c) = (Lit("a"), Lit("b"), Lit("c"))

    x = And(a, Or(b, c))

    print(x.to_cnf())

    cnf = x.to_cnf().is_cnf()
    print(cnf)
