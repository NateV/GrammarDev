# -*- coding: utf-8 -*-

from parsimonious import Grammar
from parsimonious import NodeVisitor
import os


# PDF to text with:
# >  pdftotext -layout -enc "UTF-8" [pdf file] [text file]

grammars = [
r"""
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
section = section_case_info /
          section_status_info /
          section_calendar_events /
          section_defendant_info /
          section_case_participants /
          section_bail_info /
          section_charges /
          section_disposition_sentencing /
          section_commonwealth_info /
          section_entries /
          section_payment_plan /
          section_case_financial_info



section_case_info = (ws* ~"CASE INFORMATION"i new_line) section_case_info_body
section_case_info_body = judge_assigned content new_line section_body
judge_assigned = ws* ~"judge assigned:"i ws* judge_name
judge_name =  (single_content_char !~"date filed"i)+ single_content_char

section_status_info = (ws* ~"STATUS INFORMATION"i new_line) section_body
section_calendar_events = (ws* ~"calendar events"i new_line)  section_body
section_defendant_info =  (ws* ~"defendant information"i new_line) section_body
section_case_participants = (ws* ~"case participants"i new_line) section_body
section_bail_info = (ws* ~"bail information"i new_line) section_body
section_charges = (ws* ~"charges"i new_line) section_body

section_disposition_sentencing = (ws* ~"disposition sentencing/penalties"i new_line) section_disposition_sentencing_body
section_disposition_sentencing_body = section_body

section_commonwealth_info =  (ws* ~"commonwealth information"i ws* ~"attorney information"i new_line) section_body
section_entries = (ws* ~"entries"i new_line)  section_body
section_payment_plan = (ws* ~"payment plan summary"i new_line) section_body
section_case_financial_info = (ws* ~"case financial information"i new_line) section_body


section_body = (line !start_of_footer)+ line


start_of_footer = (ws* ~"CPCMS 9082" content new_line)
footer = start_of_footer line+

line = content new_line?

single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
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
section = section_case_info /
          section_status_info /
          section_calendar_events /
          section_defendant_info /
          section_case_participants /
          section_bail_info /
          section_charges /
          section_disposition_sentencing /
          section_commonwealth_info /
          section_entries /
          section_payment_plan /
          section_case_financial_info



section_case_info = (ws* ~"CASE INFORMATION"i new_line) section_case_info_body
section_case_info_body = judge_assigned content new_line section_body
judge_assigned = ws* ~"judge assigned:"i ws* judge_name
judge_name =  (single_content_char !~"date filed"i)+ single_content_char

section_status_info = (ws* ~"STATUS INFORMATION"i new_line) section_body
section_calendar_events = (ws* ~"calendar events"i new_line)  section_body
section_defendant_info =  (ws* ~"defendant information"i new_line) section_body
section_case_participants = (ws* ~"case participants"i new_line) section_body
section_bail_info = (ws* ~"bail information"i new_line) section_body
section_charges = (ws* ~"charges"i new_line) section_body
section_disposition_sentencing = (ws* ~"disposition sentencing/penalties"i new_line) section_body
section_commonwealth_info =  (ws* ~"commonwealth information"i ws* ~"attorney information"i new_line) section_body
section_entries = (ws* ~"entries"i new_line)  section_body
section_payment_plan = (ws* ~"payment plan summary"i new_line) section_body
section_case_financial_info = (ws* ~"case financial information"i new_line) section_body


section_body = (line !start_of_footer)+ line


start_of_footer = (ws* ~"CPCMS 9082" content new_line)
footer = start_of_footer line+

line = content new_line?

single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
section_case_info_body = judge_assigned date_filed initiation_date
judge_assigned = "Judge Assigned:" ws* (content !date_filed)* content ws*
date_filed = "Date Filed:" ws* "05/19/2011" ws*
initiation_date = "Initiation Date:" ws* "05/19/2011"
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
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
section = section_case_info /
          section_status_info /
          section_calendar_events /
          section_defendant_info /
          section_case_participants /
          section_bail_info /
          section_charges /
          section_disposition_sentencing /
          section_commonwealth_info /
          section_entries /
          section_payment_plan /
          section_case_financial_info



section_case_info = (ws* ~"CASE INFORMATION"i new_line) section_case_info_body
section_case_info_body = ws* ~"judge assigned:"i content ~"date filed" content ~"Initiation Date:"i content new_line section_body


section_status_info = (ws* ~"STATUS INFORMATION"i new_line) section_body
section_calendar_events = (ws* ~"calendar events"i new_line)  section_body
section_defendant_info =  (ws* ~"defendant information"i new_line) section_body
section_case_participants = (ws* ~"case participants"i new_line) section_body
section_bail_info = (ws* ~"bail information"i new_line) section_body
section_charges = (ws* ~"charges"i new_line) section_body
section_disposition_sentencing = (ws* ~"disposition sentencing/penalties"i new_line) section_body
section_commonwealth_info =  (ws* ~"commonwealth information"i ws* ~"attorney information"i new_line) section_body
section_entries = (ws* ~"entries"i new_line)  section_body
section_payment_plan = (ws* ~"payment plan summary"i new_line) section_body
section_case_financial_info = (ws* ~"case financial information"i new_line) section_body


section_body = (line !start_of_footer)+ line


start_of_footer = (ws* ~"CPCMS 9082" content new_line)
footer = start_of_footer line+

line = content new_line?

content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
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
""",
r"""
docket = page+
page = header body footer page_break?
header = ws* ~"COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY"i new_line line docket_number line line line line caption
docket_number = content new_line?
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line
body = (line !(ws* ~"CPCMS 9082" content new_line))+ line
footer = line+
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
docket = page+
page = header body footer page_break?
header = ws* ~"COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY"i new_line line docket_number line line line line caption
docket_number = content new_line?
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line
body = section+ / line / (line body)
section = section_header line+
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
footer = ws* "Information Act may be subject to civil liability as set forth in 18 Pa.C.S. Section 9183." new_line?
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
docket = page+
page = header body page_break?
header = ws* ~"COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY"i new_line line docket_number line line line line caption
docket_number = content new_line?
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line
body = line+
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
docket = page+
page = header body page_break?
header = caption / (line header)
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line
body = line+
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
ws = " "
page_break = "\f" / ~"\Z"
""",
r"""
page = header body
header = caption / (line header)
caption = commonwealth_line line line defendant_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i ws* new_line
defendant_line = content new_line
body = line+
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
ws = " "
""",
r"""
docket = page+
page = page_break? header body
header = (line &(!commonwealth_line))+ commonwealth_line
commonwealth_line = ws* ~"Commonwealth of Pennsylvania"i new_line
body = line+
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
ws = " "
""",
r"""
docket = page+
page = line+ page_break?
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
""",
r"""
doc = section+
section = ~"§" ws*
ws = " "
""",
r"""
doc = section+
section = ~"a" ws*
ws = " "
""",
r"""
docket = page+
page = line+ page_break?
line = content new_line?
content = ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]*"i
new_line = "\n"
page_break = "\f"
""",
r"""
docket = page+
page = heading body
heading = ws* court_name ws* new_line

court_name = "COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY"
ws = " "
new_line = "\n"
"""
]

texts = [
"""Judge Assigned: Beloff, Adam                                                      Date Filed: 05/19/2011                  Initiation Date: 05/19/2011""",
"""§ § § §""",
"""a a a a""",
"""


CPCMS 9082                                                                                                                                              Printed: 12/20/2014

           Recent entries made in the court filing offices may not be immediately reflected on these docket sheets. Neither the courts of the Unified Judicial
           System of the Commonwealth of Pennsylvania nor the Administrative Office of Pennsylvania Courts assume any liability for inaccurate or delayed
          data, errors or omissions on these reports. Docket Sheet information should not be used in place of a criminal history background check which can
          only be provided by the Pennsylvania State Police. Moreover an employer who does not comply with the provisions of the Criminal History Record
                                         Information Act may be subject to civil liability as set forth in 18 Pa.C.S. Section 9183.
                    COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY
                                                                            DOCKET
                                                                                                        Docket Number: CP-51-CR-0000101-2011
                                                                                                                               CRIMINAL DOCKET
                                                                                                                                                         Court Case


                                                               Commonwealth of Pennsylvania
                                                                                                                                                         Page 18 of 18
                                                                           v.
                                                                    Susan Tangradi
     ** - Indicates assessment is subrogated




CPCMS 9082                                                                                                                                             Printed: 12/20/2014

          Recent entries made in the court filing offices may not be immediately reflected on these docket sheets. Neither the courts of the Unified Judicial
          System of the Commonwealth of Pennsylvania nor the Administrative Office of Pennsylvania Courts assume any liability for inaccurate or delayed
         data, errors or omissions on these reports. Docket Sheet information should not be used in place of a criminal history background check which can
         only be provided by the Pennsylvania State Police. Moreover an employer who does not comply with the provisions of the Criminal History Record
                                        Information Act may be subject to civil liability as set forth in 18 Pa.C.S. Section 9183.

""",
"""          Recent entries made in the court filing offices may not be immediately reflected on these docket sheets. Neither the courts of the Unified Judicial
          System of the Commonwealth of Pennsylvania nor the Administrative Office of Pennsylvania Courts assume any liability for inaccurate or delayed
         data, errors or omissions on these reports. Docket Sheet information should not be used in place of a criminal history background check which can
         only be provided by the Pennsylvania State Police. Moreover an employer who does not comply with the provisions of the Criminal History Record
                                        Information Act may be subject to civil liability as set forth in 18 Pa.C.S. Section 9183.
                      COURT OF COMMON PLEAS OF PHILADELPHIA COUNTY
                                                                              DOCKET
                                                                                                          Docket Number: CP-51-CR-0000101-2011
                                                                                                                                 CRIMINAL DOCKET
                                                                                                                                                           Court Case
"""

]

class CaseInfoVisitor(NodeVisitor):
  def generic_visit(self, node, vc):
    return self.stringify(vc)

  def visit_judge_assigned(self, node, vc):
    print("visiting visit_judge_assigned.")
    return self.stringify(vc)

  def visit_content(self,node,vc):
    return node.text

  def stringify(self, listed_content):
    print("stringify")
    print(listed_content)
    if isinstance(listed_content, list):
      return " ".join(listed_content)
    else:
      return listed_content

class GenericVisitor(NodeVisitor):
  def generic_visit(self,node,vc):
    return node.text

class SectionVisitor(NodeVisitor):
  def visit_doc(self, node, vc):
    return vc

  def generic_visit(self, node, vc):
    return vc

  def visit_section(self, node, vc):
    return node.text

class DocketVisitor_2(NodeVisitor):
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
#    print("visiting section.")
    return self.stringify_list(vc)

# Methods related to the Case Information section
  def visit_section_case_info(self, node, vc):
    print("visiting section case info")
    contents = self.stringify_list(vc)
    section_name = "Case_Information"
    contents = " <section name='%s'> %s </section> " % (section_name, contents)
    return contents

  def visit_section_case_info_body(self, node, vc):
    print("Visiting Section case_info body.")
    contents = self.stringify_list(vc)
    return contents

  def visit_judge_assigned(self, node, vc):
#    print("visit_judge_assigned")
    print(node.text)
    contents = self.stringify_list(vc)
    return ("<judge_assigned> %s </judge_assigned>" % contents)

  def visit_judge_name(self, node, vc):
#    print("visit_judge_name")
    print(vc)
    contents = self.stringify_list(vc)
    return contents

#Methods for status info section
  def visit_section_status_info(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Status_Information"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods for calendar events section
  def visit_section_calendar_events(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Calendar_Events"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods for defendant info section
  def visit_section_defendant_info(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Defendant_Information"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods for case participants section
  def visit_section_case_participants(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Case_Participants"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods for Bail info section
  def visit_section_bail_info(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Bail_Information"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods for charges section
  def visit_section_charges(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Charges"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods related to the Disposition Sentencing Section
  def visit_section_disposition_sentencing(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Disposition_Sentencing_Penalties"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods related to the Commonwealth Info Section
  def visit_section_commonwealth_info(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Commonwealth_Information"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods related to the Entries Section
  def visit_section_entries(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Entries"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods related to the Payment Plan Section
  def visit_section_payment_plan(self, node, vc):
    contents = self.stringify_list(vc)
    section_name = "Payment_Plan"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Methods related to the Case Financial Information Section
  def visit_section_case_financial_info(self, node, vc):
    print("Visiting section financial info.")
    contents = self.stringify_list(vc)
    section_name = "Financial_Information"
    return("<section name='%s'> %s </section>" % (section_name, contents))

#Terminals
  def visit_section_header(self,node, vc):
    return node.text

  def visit_new_line(self, node, vc):
    return node.text

  def visit_content(self, node, vc):
    return node.text

  def visit_single_content_char(self, node, vc):
    return node.text

  #Private method, if that were possible in python.
  def stringify_list(self, list):
    output = ""
    for element in list:
      output += element
    return output
# End of Class

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

test_num = 0

# grammar = Grammar(grammars[test_num])
# root = grammar.parse(texts[0])
# print("Parsed okay.")
# visitor = CaseInfoVisitor()
# results = visitor.visit(root)
# print(results)
# for r in results:
#   print(r)
# print(root.prettily())

#with open("./sample_dockets/CP-51-CR-0000001-2011.txt") as f:
with open("./sample_dockets/CP-51-CR-0005727-2011.txt") as f:
  grammar = Grammar(grammars[test_num])
  root = grammar.parse(f.read())
  visitor = DocketVisitor_2()
  print("Parse succeeded.")
  with open("output2.txt", 'w+') as f2:
    f2.write(visitor.visit(root))
  f2.close()
f.close()

