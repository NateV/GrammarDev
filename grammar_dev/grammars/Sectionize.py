from parsimonious import NodeVisitor
from parsimonious import Grammar


class DocketVisitor(NodeVisitor):
  def generic_visit(self, node, vc):
    return self.stringify_list(vc)

  def visit_docket(self, node, vc):
    docket = " <docket> %s </docket> " % self.stringify_list(vc)
    return docket

  def visit_page(self, node, vc):
    page = " <page> %s </page> " % self.stringify_list(vc)
    return page

  def visit_caption(self, node, vc):
#    print("visiting caption.")
    line = " <caption> %s </caption> " % self.stringify_list(vc)
    return line

  def visit_commonwealth_line(self, node, vc):
    line = " <state> %s </state> " % node.text
    return line

  def visit_defendant_line(self, node, vc):
#    print("visiting defendant line.")
    defendant = " <defendant> %s </defendant> " % self.stringify_list(vc)
    return defendant

  def visit_docket_number(self, node, vc):
    docket = self.stringify_list(vc)
#    print("visiting docket number.")
#    print(docket)
    try:
      index = docket.index(":")
#      print(index)
      docket = "%s <docket_number> %s </docket_number> " % (docket[0:index+1], docket[index+1:])
    except:
#      print("index not found.")
      docket = " <docket_number> % s</docket_number> " % docket
    return docket

  def visit_body(self, node, vc):
    body = " <body> %s </body> " % self.stringify_list(vc)
    return body

  def visit_footer(self, node, vc):
    footer = self.stringify_list(vc)
    footer = " <footer> %s </footer> " % footer
    return footer

  def visit_section(self, node, vc):
    section = self.stringify_list(vc)
    section_name = vc[0]
    section = " <section name='%s'> %s </section> " % (section_name.strip(), section)
    return section

  def visit_section_header(self,node, vc):
    return node.text

  def visit_new_line(self, node, vc):
    return node.text

  def visit_content(self, node, vc):
    return node.text

  #Private method, if that were possible in python.
  def stringify_list(self, list):
    output = ""
    for element in list:
      output += element
    return output
# End of Class


grammar = r"""
docket = page+
page = header body? footer page_break?

header = ws* ~"COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY"i new_line line docket_number line line line line caption
docket_number = content new_line?
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line


body = ((section !start_of_footer)* section) /
       ((line !start_of_footer)* line) /
       (line body)
section = section_header (line !start_of_footer)+ line
section_header = (ws* ~"CASE INFORMATION"i new_line) /
                 (ws* ~"STATUS INFORMATION"i new_line) /
                 (ws* ~"calendar events"i new_line) /
                 (ws* ~"defendant information"i new_line) /
                 (ws* ~"case participants"i new_line) /
                 (ws* ~"bail information"i new_line) /
                 (ws* ~"charges"i new_line) /
                 (ws* ~"disposition sentencing/penalties"i new_line) /
                 (ws* ~"commonwealth information"i ws* ~"attorney information"i new_line) /
                 (ws* ~"entries"i new_line) /
                 (ws* ~"payment plan summary"i new_line) /
                 (ws* ~"case financial information"i new_line)

start_of_footer = (ws* ~"CPCMS 9082" content new_line)
footer = start_of_footer line+

line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
"""



