def indent_str(level): return " " * (level)
def format_tree(node): return node.tree_str(0)

class Node(object):

    # top level CNF conversion
    def to_cnf(self):
        tree = self._to_cnf(Lit.new_internal())
        return tree

    def to_clauses(self):
        conv = CNFConverter(self)
        return conv.go()

    def _to_cnf(self): raise RuntimeError("not implemented in base class")
    def is_leaf(self): raise RuntimeError("not implemented in base class")

class UnaryNode(Node):
    def __init__(self, oper_str, arg):
        self.oper_str = oper_str
        self.children = [ arg ]

    def __str__(self): return "%s%s" % (self.oper_str, self.children[0])
    def is_leaf(self): return False

    def tree_str(self, level):
        return "%s%s\n%s" % \
                (indent_str(level), self.oper_str, self.children[0].tree_str(level + 1))

class Not(UnaryNode):
    def __init__(self, arg):
        super(Not, self).__init__("~", arg)

    def _to_cnf(self, witness):
        return Not(self.children[0]._to_cnf(witness))

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
    def tree_str(self, level): return "%s%s" % (indent_str(level), str(self))
    def is_leaf(self): return True

    @staticmethod
    def new_internal():
        l = Lit("_x%d" % Lit.SERIAL, True)
        Lit.SERIAL += 1
        return l

class BinaryNode(Node):

    def __init__(self, oper_str, left, right):
        print("Binary node ctor")
        self.oper_str = oper_str
        self.children = [left, right]

    def __str__(self):
        return "%s %s %s" % (self.children[0], self.oper_str, self.children[1])

    def tree_str(self, level):
        return "%s%s\n%s\n%s" % (
                indent_str(level),
                self.oper_str,
                self.children[0].tree_str(level + 1),
                self.children[1].tree_str(level + 1)
                )

    def is_leaf(self): return False

class And(BinaryNode):

    def __init__(self, left, right):
        print("And constructor: %s")
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

class Clause(object):
    """ A flat clause """
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return " + ".join([ str(i) for i in self.items ])

class ClauseList(object):
    def __init__(self, clauses):
        self.clauses = clauses

    def __str__(self):
        return "Clause list (len=%d):\n" % (len(self.clauses)) + \
                "\n".join([ "  " + str(i) for i in self.clauses ])

# XXX more descriptive name
class CNFConverter(object):
    """ Converts a CNF tree into flat clauses """
    def __init__(self, tree):
        self.tree = tree
        self._cur_clause = [] # unwrapped
        self.clauses = []

    def go(self):
        self._to_clauses(self.tree)
        return ClauseList(self.clauses)

    def _to_clauses(self, node):

            if isinstance(node, And):
                for child in node.children:
                    collecting = not isinstance(child, And)
                    self._to_clauses(child)
                    if collecting:
                        self.clauses.append(Clause(self._cur_clause))
                        self._cur_clause = []
            elif isinstance(node, Or):
                for child in node.children: self._to_clauses(child)
            elif isinstance(node, Lit) or isinstance(node, Not):
                 # Note that a Not must have Lit as child in CNF
                self._cur_clause.append(node)
            else:
                raise RuntimeError("Unknown node type: %s" % type(node))


# XXX just a test
if __name__ == "__main__":
    (a, b, c) = (Lit("a"), Lit("b"), Lit("c"))

    x = And(a, Or(b, c))

    cnf = x.to_cnf()
    print(cnf)
    print(format_tree(cnf))
    clauses = cnf.to_clauses()
    print(clauses)
