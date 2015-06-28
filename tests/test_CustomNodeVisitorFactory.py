from parsimonious import Grammar
from grammar_dev.grammars.CustomNodeVisitorFactory import CustomVisitorFactory


def test_custom_visitor_factory():
  text = """Hi there, partner"""
  grammar = r"""
  text = greeting punctuation identifier
  greeting = hi_there?
  punctuation = comma?
  identifier = partner?

  hi_there = "Hi there"
  comma = ", "
  partner = "partner"
  """
  grammar = Grammar(grammar)
  terminals = ["hi_there", "comma", "partner"]
  nonterminals = ["text", "greeting", "punctuation", "identifier"]
  custom_visitor = CustomVisitorFactory(terminals, nonterminals, dict()).create_instance()
  #custom_visitor = custom_visitor.create_instance()
  root = grammar.parse(text)
#   print("The parse tree:")
#   print(root.prettily())
  xml = custom_visitor.visit(root)
  assert xml=="<text> <greeting> Hi there </greeting><punctuation> ,  </punctuation><identifier> partner </identifier> </text>"
#   print(xml)
#   print("Finished.")