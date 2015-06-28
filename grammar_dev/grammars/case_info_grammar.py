from parsimonious import Grammar
from parsimonious import NodeVisitor
from grammar_dev.grammars.CustomNodeVisitorFactory import CustomVisitorFactory

grammars = [
r"""
# Nonterminals
case_info = (new_line? assigned_filed_initiated the_rest) /
            (new_line? line assigned_filed_initiated the_rest) /
            (new_line? line line assigned_filed_initiated the_rest)
assigned_filed_initiated = ws* judge_assigned ws ws ws+ date_filed ws ws ws+ date_initiated ws* new_line

judge_assigned = judge_assigned_label ws judge_assigned_name?
judge_assigned_name =  (single_content_char !(ws ws))+ single_content_char

date_filed = date_filed_label ws date_filed_date  #"Date Filed: 01/03/2011"
date_filed_date = date &ws

date_initiated = date_initiated_label ws date_initiated_date     #"Initiation Date: 01/03/2011"
date_initiated_date = date &new_line

the_rest = line*

# Silent helper nonterminals (don't include in list of terminals)
line = single_content_char* new_line?
date = number forward_slash number forward_slash number

# Silent Terminals (should be consumed and not returned. Don't include
# in list of terminals.)
judge_assigned_label = "Judge Assigned:"
date_filed_label = "Date Filed:"
date_initiated_label = "Initiation Date:"

# Loud Terminals (include in list of terminals)
number = ~"[0-9]"+
forward_slash = "/"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
ws = " "
""",
r"""
# Nonterminals
case_info = new_line? line* new_line*
line = single_content_char* new_line

# Terminals
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
"""
]

nonterminals = ["case_info", "judge_assigned",
                "date_filed", "date_initiated", "the_rest"]
terminals = ["single_content_char", "new_line", "judge_assigned_name",
             "number", "forward_slash"]

def parse(section_text):

  grammar = Grammar(grammars[0])
  custom_visitor = CustomVisitorFactory(terminals, nonterminals, dict()).create_instance()
  root = grammar.parse(section_text)
#   print("Parse tree:")
#   print(root.prettily())
  xml = custom_visitor.visit(root)
  # print(xml)
  return xml
