from parsimonious import NodeVisitor

def stringify(node_visitor, content):
  return "".join(content)

def generic_visit(node_visitor, node, vc):
  return node_visitor.stringify(vc)

class CustomVisitorFactory:
    """
    This class creates an object k that is an instance of a custom
    subclass of parsimonious' NodeVisitor class.
    """

    def __init__(self, terminals, non_terminals, non_default_methods):
        """
        Input: a) list of terminal symbols,
               b) list of non-terminal symbols, and
               c) dict of methods to override the default methods
                  this class creates.
        Inside: Sets these as attributes of the instance of the class.
        """
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.non_default_methods = non_default_methods

    def create_subclass(self, subclass_name = "CustomVisitor"):
        """
        Input: Optionally, a name for the subclass
        Output: A subclass of NodeVisitor with certain default terminal and
                non-terminal methods.
        """
        custom_methods = dict()
        custom_methods["stringify"] = stringify
        custom_methods["generic_visit"] = generic_visit

        method_name = "visit_{}"
        for terminal in self.terminals:
            if terminal not in self.non_default_methods:
                custom_methods[method_name.format(terminal)] = self.generate_default_terminal_method(terminal)

        for non_terminal in self.non_terminals:
            if non_terminal not in self.non_default_methods:
                custom_methods[method_name.format(non_terminal)] = self.generate_default_non_terminal_method(non_terminal)

        for symbol, method in self.non_default_methods:
            custom_methods[method_name.format(symbol)] = method

        return type("CustomVisitor", (NodeVisitor,), custom_methods)

    def create_instance(self, class_name = "CustomVisitor"):
       """
       Input: an optional name for the custom class to be created.
       Output: an instance of the subclass of NodeVisitor. Uses the instance
               method NodeVisitor#create_subclass()
       """
       CustomVisitor = self.create_subclass(class_name)
       return CustomVisitor()

    # Default method generators
    def generate_default_terminal_method(self, terminal):
        return lambda self, node, children: self.stringify(node.text)


    def generate_default_non_terminal_method(self, non_terminal_name):
        def non_terminal_method(self, node, children):
            contents = self.stringify(children)
            return "<%s> %s </%s>" % (non_terminal_name, contents, non_terminal_name)
        return non_terminal_method



