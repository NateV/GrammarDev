from parsimonious import Grammar
from parsimonious import NodeVisitor
from lxml import etree
import io
import re
import pytest

grammars = [
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer?


disposition_subsection = (disposition_type disposition_details) / (heading new_line*)
disposition_type = !ws !first_heading_line single_content_char_no_ws content new_line

disposition_details = ws ws+ !start_of_footer case_event+

  ####Imported from dispositionDetailsSection.py ###########
  case_event = new_line? case_event_desc_and_date sequences new_line?

  case_event_desc_and_date = ws* case_event_desc ws ws+ date ws ws ws+ is_final new_line
  case_event_desc = (word ws)+

  date = number forward_slash number forward_slash number
  is_final = (word ws word) / word

  sequences = sequence+
  sequence = sequence_start sequence_details?
  sequence_start = ws+ sequence_number ws forward_slash ws sequence_description ws ws ws ws+ offense_disposition ws ws ws+ grade? ws* code_section new_line
  sequence_number = number+ &ws
  sequence_description = (word ws)+
  offense_disposition = (word ws)+
  code_section = single_content_char+


    #### Imported from sequenceDetailsSection.py #######
    sequence_details = !sequence_start sequence_description_continued* things_a_judge_did*

    # The complexity of the following rule is necessary because I need to
    # distinguish lines that carry over from the sequence description, which
    # could be just words without commas: "intent to distribute"
    # or which can contain commas, as in
    # "    Replaced by 18 § 2701 §§ A3, Simple Assault"
    # I identify names by [words] comma [words], as in "Smith, John"
    # In order to distinguish them, I'm assuming that a judge won't have more
    # than two last names before the comma, and a sequence_description_continued line will
    # have at least three words before any comma.
    # N.B. If this turns out to be wrong, a couple other ideas might work:
    # 1) Treat the "Replaced by" lines as an entirely separate optional line,
    #    characterized by the presence of section symbols
    # 2) Create a dictionary of judges' names, and explicitly check their names.
    sequence_description_continued = (ws+ !number !name_line word_no_comma new_line) /
                                     (ws+ !number !name_line word_no_comma ws word_no_comma new_line) /
                                     (ws+ !number !name_line word_no_comma ws word_no_comma  ws content new_line) /
                                     (ws+ !number !name_line word_no_comma comma ws word_no_comma ws word_no_comma (ws !date word_no_comma)* new_line)


    things_a_judge_did = name_line sentence_info*
    sentence_info = !name_line program_length_start extra_sentence_details?

    name_line = ws+ judge_name ws ws ws ws+ date new_line
    judge_name = word_no_comma (ws word_no_comma)? comma ws word_no_comma (ws word_no_comma)? (ws word_no_comma)?

    program_length_start = (ws ws+ no_further_penalty new_line) /
                           (ws ws+ program ws ws+ length_of_sentence (ws ws+ date)? new_line)
    program = word (ws word)*

    extra_sentence_details = (!name_line !program_length_start !sequence_start line)*


    length_of_sentence = word_or_numbers_or_fraction &(ws / new_line)
    word_or_numbers_or_fraction = (word ws word_or_numbers_or_fraction) /
                                  (fraction ws word_or_numbers_or_fraction) /
                                  (number ws word_or_numbers_or_fraction) /
                                  (word)/
                                  (number)/
                                  (fraction)

    fraction = number forward_slash number
  ####End Imported From dispositionDetailsSection.py

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line


footer = start_of_footer line+
start_of_footer = (" LINKED SENTENCES:" new_line) /
                  (ws* "The following Judge Ordered Conditions are imposed:" new_line)

word_no_comma = single_char_no_comma_or_ws+
word = single_content_char_no_ws+

##Terminals
grade = ~"[a-z0-9]"i+
no_further_penalty = ~"No Further Penalty"i
single_char_no_comma_or_ws = ~"[a-z0-9`\"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
line = content new_line?
content = single_content_char+
content_no_comma = single_content_char_no_comma+
content_no_ws = single_content_char_no_ws+
number = ~"[0-9,\.]+"
forward_slash = "/"
single_content_char_no_comma =  ~"[a-z0-9`\ \"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_letter_no_ws = ~"[a-z]"i
comma = ","
new_line = "\n"
ws = " "
""",
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer?


disposition_subsection = (disposition_type disposition_details) / (heading new_line*)
disposition_type = !ws !first_heading_line single_content_char_no_ws content new_line

disposition_details = ws ws+ !start_of_footer case_event+

  ####Imported from dispositionDetailsSection.py ###########
  case_event = new_line? case_event_desc_and_date sequences new_line?

  case_event_desc_and_date = ws* case_event_desc ws ws+ date ws ws ws+ is_final new_line
  case_event_desc = (word ws)+

  date = number forward_slash number forward_slash number
  is_final = (word ws word) / word

  sequences = sequence+
  sequence = sequence_start sequence_details?
  sequence_start = ws+ sequence_number ws forward_slash ws sequence_description ws ws ws ws+ offense_disposition ws ws ws+ grade? ws* code_section new_line
  sequence_number = number+ &ws
  sequence_description = (word ws)+
  offense_disposition = (word ws)+
  code_section = single_content_char+


    #### Imported from sequenceDetailsSection.py #######
    sequence_details = !sequence_start sequence_description_continued* things_a_judge_did*

    # The complexity of the following rule is necessary because I need to
    # distinguish lines that carry over from the sequence description, which
    # could be just words without commas: "intent to distribute"
    # or which can contain commas, as in
    # "    Replaced by 18 § 2701 §§ A3, Simple Assault"
    # I identify names by [words] comma [words], as in "Smith, John"
    # In order to distinguish them, I'm assuming that a judge won't have more
    # than two last names before the comma, and a sequence_description_continued line will
    # have at least three words before any comma.
    # N.B. If this turns out to be wrong, a couple other ideas might work:
    # 1) Treat the "Replaced by" lines as an entirely separate optional line,
    #    characterized by the presence of section symbols
    # 2) Create a dictionary of judges' names, and explicitly check their names.
    sequence_description_continued = (ws+ !name_line word_no_comma new_line) /
                                     (ws+ !name_line word_no_comma ws word_no_comma new_line) /
                                     (ws+ !name_line word_no_comma ws word_no_comma  ws content new_line) /
                                     (ws+ !name_line word_no_comma comma ws word_no_comma ws word_no_comma ws content new_line)


    things_a_judge_did = name_line sentence_info*
    sentence_info = !name_line program_length_start extra_sentence_details?

    name_line = ws+ judge_name ws ws ws ws+ date new_line
    judge_name = word_no_comma (ws word_no_comma)? comma ws word_no_comma (ws word_no_comma)?
    #judge_name = word_no_comma (ws word_no_comma)? comma ws word_no_comma (ws word_no_comma)?

    program_length_start = (ws ws+ no_further_penalty new_line) /
                           (ws ws+ program ws ws+ length_of_sentence (ws ws+ date)? new_line)
    program = word (ws word)*

    extra_sentence_details = (!name_line !program_length_start !sequence_start line)*


    length_of_sentence = word_or_numbers_or_fraction &(ws / new_line)
    word_or_numbers_or_fraction = (word ws word_or_numbers_or_fraction) /
                                  (fraction ws word_or_numbers_or_fraction) /
                                  (number ws word_or_numbers_or_fraction) /
                                  (word)/
                                  (number)/
                                  (fraction)

    fraction = number forward_slash number
  ####End Imported From dispositionDetailsSection.py

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line


footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

word_no_comma = single_char_no_comma_or_ws+
word = single_content_char_no_ws+

##Terminals
grade = ~"[a-z0-9]"i+
no_further_penalty = ~"No Further Penalty"i
single_char_no_comma_or_ws = ~"[a-z0-9`\"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
line = content new_line?
content = single_content_char+
content_no_comma = single_content_char_no_comma+
content_no_ws = single_content_char_no_ws+
number = ~"[0-9,\.]+"
forward_slash = "/"
single_content_char_no_comma =  ~"[a-z0-9`\ \"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_letter_no_ws = ~"[a-z]"i
comma = ","
new_line = "\n"
ws = " "
""",
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer?


disposition_subsection = (disposition_type disposition_details) / (heading new_line*)
disposition_type = !ws !first_heading_line single_content_char_no_ws content new_line

disposition_details = ws ws+ !start_of_footer case_event+

  ####Imported from dispositionDetailsSection.py ###########
  case_event = new_line? case_event_desc_and_date sequences new_line?

  case_event_desc_and_date = ws* case_event_desc ws ws+ date ws ws ws+ is_final new_line
  case_event_desc = (word ws)+

  date = number forward_slash number forward_slash number
  is_final = (word ws word) / word

  sequences = sequence+
  sequence = sequence_start sequence_details?
  sequence_start = ws+ sequence_number ws forward_slash ws sequence_description ws ws ws ws+ offense_disposition ws ws ws+ grade? ws* code_section new_line
  sequence_number = number+ &ws
  sequence_description = (word ws)+
  offense_disposition = (word ws)+
  code_section = single_content_char+


    #### Imported form sequenceDetailsSection.py #######
    sequence_details = !sequence_start sequence_description_continued* things_a_judge_did*


    sequence_description_continued = (ws+ !name_line word_no_comma new_line) /
                                     (ws+ !name_line word_no_comma ws word_no_comma new_line) /
                                     (ws+ !name_line word_no_comma ws word_no_comma  ws content new_line) /
                                     (ws+ !name_line word_no_comma comma ws word_no_comma ws word_no_comma ws content new_line)

    things_a_judge_did = name_line sentence_info*
    sentence_info = !name_line program_length_start extra_sentence_details?

    name_line = ws+ judge_name ws ws ws ws+ date new_line
    judge_name = word_no_comma (ws word_no_comma)? comma ws word_no_comma (ws word_no_comma)?
    #judge_name = word_no_comma (ws word_no_comma)? comma ws word_no_comma (ws word_no_comma)?

    program_length_start = (ws ws+ no_further_penalty new_line) /
                           (ws ws+ program ws ws+ length_of_sentence (ws ws+ date)? new_line)
    program = word (ws word)*

    extra_sentence_details = (!name_line !program_length_start !sequence_start line)*


    length_of_sentence = word_or_numbers_or_fraction &(ws / new_line)
    word_or_numbers_or_fraction = (word ws word_or_numbers_or_fraction) /
                                  (fraction ws word_or_numbers_or_fraction) /
                                  (number ws word_or_numbers_or_fraction) /
                                  (word)/
                                  (number)/
                                  (fraction)

    fraction = number forward_slash number
  ####End Imported From dispositionDetailsSection.py

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line


footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

word_no_comma = single_char_no_comma_or_ws+
word = single_content_char_no_ws+

##Terminals
grade = ~"[a-z0-9]"i+
no_further_penalty = ~"No Further Penalty"i
single_char_no_comma_or_ws = ~"[a-z0-9`\"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
line = content new_line?
content = single_content_char+
content_no_comma = single_content_char_no_comma+
content_no_ws = single_content_char_no_ws+
number = ~"[0-9,\.]+"
forward_slash = "/"
single_content_char_no_comma =  ~"[a-z0-9`\ \"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_letter_no_ws = ~"[a-z]"i
comma = ","
new_line = "\n"
ws = " "
""",
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer?


disposition_subsection = (disposition_type disposition_details) / (heading new_line*)
disposition_type = !ws !first_heading_line single_content_char_no_ws content new_line

disposition_details = ws ws+ !start_of_footer case_event+

  ####Imported from dispositionDetailsSection.py ###########
  case_event = new_line? case_event_desc_and_date sequences new_line?

  case_event_desc_and_date = ws* case_event_desc ws ws+ date ws ws ws+ is_final new_line
  case_event_desc = (word ws)+

  date = number forward_slash number forward_slash number
  is_final = (word ws word) / word

  sequences = sequence+
  sequence = sequence_start sequence_details?
  sequence_start = ws+ sequence_number ws forward_slash ws sequence_description ws ws ws ws+ offense_disposition ws ws ws+ grade? ws* code_section new_line
  sequence_number = number+ &ws
  sequence_description = (word ws)+
  offense_disposition = (word ws)+
  code_section = single_content_char+


    #### Imported form sequenceDetailsSection.py #######
    sequence_details = !sequence_start sequence_description_continued? things_a_judge_did*


    sequence_description_continued = ws+ !name_line content_no_comma new_line

    things_a_judge_did = name_line sentence_info*
    sentence_info = !name_line program_length_start extra_sentence_details?

    name_line = ws+ judge_name ws ws ws ws+ date new_line
    judge_name = word_no_comma comma ws word_no_comma

    program_length_start = (ws ws+ no_further_penalty new_line) /
                           (ws ws+ program ws ws+ length_of_sentence (ws ws+ date)? new_line)
    program = word (ws word)*

    extra_sentence_details = (!name_line !program_length_start !sequence_start line)*


    length_of_sentence = word_or_numbers_or_fraction &(ws / new_line)
    word_or_numbers_or_fraction = (word ws word_or_numbers_or_fraction) /
                                  (fraction ws word_or_numbers_or_fraction) /
                                  (number ws word_or_numbers_or_fraction) /
                                  (word)/
                                  (number)/
                                  (fraction)

    fraction = number forward_slash number
  ####End Imported From dispositionDetailsSection.py

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line


footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

word_no_comma = single_char_no_comma_or_ws+
word = single_content_char_no_ws+

##Terminals
grade = ~"[a-z0-9]"i+
no_further_penalty = ~"No Further Penalty"i
single_char_no_comma_or_ws = ~"[a-z0-9`\"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
line = content new_line?
content = single_content_char+
content_no_comma = single_content_char_no_comma+
content_no_ws = single_content_char_no_ws+
number = ~"[0-9,\.]+"
forward_slash = "/"
single_content_char_no_comma =  ~"[a-z0-9`\ \"=_\.\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_letter_no_ws = ~"[a-z]"i
comma = ","
new_line = "\n"
ws = " "
""",
r"""
sequence = sequence_description judge_date* sentence_program_info? new_line?
sequence_description = ((ws ws ws ws ws ws number ws forward_slash ws line) (ws ws ws ws ws ws seq_desc_continued)* ) /
                       ((ws ws ws ws number ws forward_slash ws line) (ws ws ws ws seq_desc_continued)*)
seq_desc_continued = !ws line

#judge_date = ws ws ws ws ws ws ws ws ws ws line
judge_date = ws ws ws ws ws ws+ judge_name ws ws ws+ date new_line
judge_name = word ~", " word
date = number forward_slash number forward_slash number

sentence_program_info = (ws ws ws ws ws ws ws ws ws ws* line)+

footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
word = ~"[a-zA-Z]*"
forward_slash = "/"
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
line = ws ws ws ws ws ws ws word "," ws word ws* "05/17/2011" new_line
word = ~"[a-zA-Z]*"
ws = " "
new_line = "\n"
""",
r"""
sequence = sequence_description judge_date* sentence_program_info? new_line?
sequence_description = ((ws ws ws ws ws ws number ws forward_slash ws line) (ws ws ws ws ws ws seq_desc_continued)* ) /
                       ((ws ws ws ws number ws forward_slash ws line) (ws ws ws ws seq_desc_continued)*)
seq_desc_continued = !ws line

#judge_date = ws ws ws ws ws ws ws ws ws ws line
judge_date = ws ws ws ws ws ws+ judge_name ws ws ws+ date new_line
judge_name = word ~", " word
date = number forward_slash number forward_slash number

sentence_program_info = (ws ws ws ws ws ws ws ws ws ws* line)+

footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
word = ~"[a-zA-Z]*"
forward_slash = "/"
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
line = ws ws ws ws ws ws ws word "," ws word ws* "05/17/2011" new_line
word = ~"[a-zA-Z]*"
ws = " "
new_line = "\n"
""",
r"""
sequence = new_line sequence_description judge_date? sentence_program_info?
sequence_description = ((ws ws ws ws ws ws number ws forward_slash ws line) (ws ws ws ws ws ws !ws line)* ) /
                       ((ws ws ws ws number ws forward_slash ws line) (ws ws ws ws !ws line)* )

judge_date = ws ws ws ws ws ws ws ws ws ws line

sentence_program_info = (ws ws ws ws ws ws ws ws ws ws ws ws ws* line)+

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
forward_slash = "/"
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer


disposition_subsection = (disposition_type case_event+ new_line*) / (heading new_line*)
disposition_type = !ws line

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line

case_event = case_event_line sequence+
case_event_line = ws ws line

sequence = sequence_description judge_date? sentence_program_info?
sequence_description = ((ws ws ws ws ws ws number ws forward_slash ws line) (ws ws ws ws ws ws !number !ws line)* ) /
                       ((ws ws ws ws number ws forward_slash ws line) (ws ws ws ws !number !ws line)*)


judge_date = ws ws ws ws ws ws ws ws ws ws line

sentence_program_info = (ws ws ws ws ws ws ws ws ws ws ws ws ws* line)+

footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
forward_slash = "/"
single_content_char_no_ws =  ~"[a-z0-9`\"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = ws* new_line? disposition_subsection+ new_line? footer


disposition_subsection = (disposition_type case_event+ new_line*) / (heading new_line*)
disposition_type = !ws line

heading = first_heading_line line line line line line
first_heading_line = ~"Disposition"i new_line

case_event = case_event_line sequence+
case_event_line = ws ws line

sequence = sequence_description judge_date? program_type*
sequence_description = (ws ws ws ws number ws forward_slash ws line) (ws ws ws ws !number line)* /
                       (ws ws ws ws ws ws number ws forward_slash ws line) (ws ws ws ws ws ws !number line)*

judge_date = ws ws ws ws ws ws ws ws ws ws line

program_type = ws ws ws ws ws ws ws ws ws ws ws ws ws* line

footer = start_of_footer line+
start_of_footer = " LINKED SENTENCES:" new_line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
forward_slash = "/"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading disposition_subsection+
heading = line line line line line line

disposition_subsection = disposition_line case_event+
disposition_line = !ws line

case_event = case_event_line sequence_description+
case_event_line = ws ws line

sequence_description = sequence_description_line judge_date? program_type*
sequence_description_line = ws ws ws ws line

judge_date = ws ws ws ws ws ws ws ws ws ws line

program_type = ws ws ws ws ws ws ws ws ws ws ws ws ws* line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading disposition_subsection+
heading = line line line line line line

disposition_subsection = disposition_line case_event+
disposition_line = !ws line

case_event = case_event_line sequence_description+
case_event_line = ws ws line

sequence_description = sequence_description_line judge_date? program_type*
sequence_description_line = ws ws ws ws line

judge_date = ws ws ws ws ws ws ws ws ws ws line

program_type = ws ws ws ws ws ws ws ws ws ws ws ws ws* line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading disposition_subsection+
heading = line line line line line line

disposition_subsection = disposition_line case_event+

disposition_line = !ws line
case_event = ws+ line

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading disposition_subsection+
heading = line line line line line line

disposition_subsection = line+

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading
heading = line line line line line line
line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
""",
r"""
section_disposition_sentencing_body = new_line? heading disposition_subsection*
heading = line line line line line line
disposition_subsection = content new_line case_event+
case_event = ws ws content new_line sequence_description+
sequence_description = ws ws ws ws number ws "/" ws content new_line (ws* !number content new_line)*

line = content new_line?
content = single_content_char+
number = ~"[0-9,]*"
single_content_char =  ~"[a-z0-9`\ \"=_\.,\-\(\)\'\$\?\*%;:#&\[\]/@§]"i
new_line = "\n"
multi_ws = ws ws
ws = " "
"""]


texts = [
r"""Lower Court Proceeding (generic)
  Preliminary Hearing                                                         12/30/2010                                    Not Final
    1 / Manufacture, Delivery, or Possession With Intent to                      Held for Court                                  F            35 § 780-113 §§ A30
    Manufacture or Deliver
    2 / Criminal Conspiracy Engaging - Manufacture,                              Held for Court                                  F            18 § 903 §§ A1
    Delivery, or Possession With Intent to Manufacture or
    Deliver
    3 / Int Poss Contr Subst By Per Not Reg                                      Held for Court                                  M            35 § 780-113 §§ A16
Proceed to Court
  Information Filed                                                           01/11/2011                                    Not Final
    1 / Manufacture, Delivery, or Possession With Intent to                      Held for Court                                  F            35 § 780-113 §§ A30
    Manufacture or Deliver
    2 / Criminal Conspiracy Engaging - Manufacture,                              Held for Court                                  F            18 § 903 §§ A1
    Delivery, or Possession With Intent to Manufacture or
    Deliver
    3 / Int Poss Contr Subst By Per Not Reg                                      Held for Court                                  M            35 § 780-113 §§ A16
Guilty Plea - Negotiated
  Trial                                                                       04/19/2011                                    Final Disposition
    1 / Manufacture, Delivery, or Possession With Intent to                      Guilty Plea - Negotiated                        F            35 § 780-113 §§ A30
    Manufacture or Deliver
       Berry, Willis W. Jr.                                                         04/19/2011
            Confinement                                                               Min of 2.00 Years                                   04/19/2011
                                                                                      Max of 4.00 Years
                                                                                      2 years - 4 years
                  The defendant is not eligible for RRRI by statute.
    2 / Criminal Conspiracy Engaging - Manufacture,                              Guilty Plea - Negotiated                        F            18 § 903 §§ A1
    Delivery, or Possession With Intent to Manufacture or
    Deliver
       Berry, Willis W. Jr.                                                         04/19/2011
            Confinement                                                               Min of 2.00 Years                                   04/19/2011
                                                                                      Max of 4.00 Years
                                                                                      2 years - 4 years
                  The defendant is not eligible for RRRI by statute.
    3 / Int Poss Contr Subst By Per Not Reg                                      Nolle Prossed                                   M            35 § 780-113 §§ A16
          Berry, Willis W. Jr.                                                      04/19/2011
""",
r"""Lower Court Proceeding (generic)
  Preliminary Hearing                                                        12/30/2010                                    Not Final
      1 / Failure to Comply With Registration of Sexual                         Held for Court                                  F1           18 § 4915 §§ A1
      Offender Requirements
      2 / Verify Address or Photographed as Required                            Held for Court                                  F1           18 § 4915 §§ A2
      3 / Provide Accurate Information                                          Held for Court                                  F1           18 § 4915 §§ A3
Proceed to Court
  Information Filed                                                          01/10/2011                                    Not Final
      1 / Failure to Comply With Registration of Sexual                         Held for Court                                  F1           18 § 4915 §§ A1
      Offender Requirements
      2 / Verify Address or Photographed as Required                            Held for Court                                  F1           18 § 4915 §§ A2
      3 / Provide Accurate Information                                          Held for Court                                  F1           18 § 4915 §§ A3
Guilty Plea - Negotiated
  Pre-Trial Conference                                                       02/17/2011                                    Final Disposition
      1 / Failure to Comply With Registration of Sexual                         Guilty Plea - Negotiated                        F1           18 § 4915 §§ A1
      Offender Requirements
         Wogan, Chris R.                                                           02/17/2011
         Confinement                                                     Min of 1.00 Years
                                                                         Max of 2.00 Years
                                                                         1 year - 2 years
             SCI Laurel Highlands is recommend. The defendant must attend Sex Offender Treatment. (No credit for
             time served) The defendant is not RRRI eligible. Parole/ Probation must be supervised by the Sex
             Offender's Unit.
        Probation                                                        Max of 5.00 Years
                                                                         5 years
       Wogan, Chris R.                                                 08/27/2014
         Confinement                                                                Min of 1.00 Years
                                                                                    Max of 3.00 Years
                                                                                    Other
         Probation                                                                  Max of 5.00 Years
                                                                                    5 years
       Wogan, Chris R.                                                           10/03/2014
         Confinement                                                               Min of 11.00 Months 15.00 Days
                                                                                   Max of 23.00 Months 15.00 Days
                                                                                   Other
               Credit to be calculated by the Phila. Prison System
               Defendant to be supervised by the Sexual Offender's Unit
         Probation                                                                  Max of 5.00 Years
                                                                                    5 years
    2 / Verify Address or Photographed as Required                            Nolle Prossed                                   F1           18 § 4915 §§ A2
       Wogan, Chris R.                                                           02/17/2011
       Wogan, Chris R.                                                           08/27/2014
       Wogan, Chris R.                                                           10/03/2014
    3 / Provide Accurate Information                                          Nolle Prossed                                   F1           18 § 4915 §§ A3
       Wogan, Chris R.                                                           02/17/2011
       Wogan, Chris R.                                                           08/27/2014
       Wogan, Chris R.                                                           10/03/2014
The following Judge Ordered Conditions are imposed:
Condition
Defendants prior Probation sentence is revoked.
Detainer Lifted
Credit for time served.
""",
r"""Lower Court Proceeding (generic)
  Preliminary Hearing                                                        12/30/2010                                    Not Final
      1 / Failure to Comply With Registration of Sexual                         Held for Court                                  F1           18 § 4915 §§ A1
      Offender Requirements
      2 / Verify Address or Photographed as Required                            Held for Court                                  F1           18 § 4915 §§ A2
      3 / Provide Accurate Information                                          Held for Court                                  F1           18 § 4915 §§ A3
Proceed to Court
  Information Filed                                                          01/10/2011                                    Not Final
      1 / Failure to Comply With Registration of Sexual                         Held for Court                                  F1           18 § 4915 §§ A1
      Offender Requirements
      2 / Verify Address or Photographed as Required                            Held for Court                                  F1           18 § 4915 §§ A2
      3 / Provide Accurate Information                                          Held for Court                                  F1           18 § 4915 §§ A3
Guilty Plea - Negotiated
  Pre-Trial Conference                                                       02/17/2011                                    Final Disposition
      1 / Failure to Comply With Registration of Sexual                         Guilty Plea - Negotiated                        F1           18 § 4915 §§ A1
      Offender Requirements and more
          Wogan, Chris R.                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
    2 / Verify Address or Photographed as Required                            Nolle Prossed                                   F1           18 § 4915 §§ A2
       Wogan, Chris R.                                                           02/17/2011
       Wogan, Chris R.                                                          08/27/2014
       Wogan, Chris R.                                                           10/03/2014
    3 / Provide Accurate Information                                          Nolle Prossed                                   F1           18 § 4915 §§ A3
       Wogan, Chris R.                                                          02/17/2011
       Wogan, Chris R.                                                           08/27/2014
       Wogan, Chris R.                                                         10/03/2014
The following Judge Ordered Conditions are imposed:
Condition
Defendants prior Probation sentence is revoked.
Detainer Lifted
Credit for time served.
""",
r"""Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                   Sentence Conditions

Lower Court Proceeding (generic)
  Preliminary Hearing                                                        05/18/2011                                    Not Final
    1 / Criminal Attempt - Escape                                             Held for Court                                  F3           18 § 901 §§ A
       Hill, Glynnis                                                             09/09/2011
         Confinement                                                               7 1/2 years to 15 years                             09/09/2011
               DEFENDANT FOUND NOT TO BE SEXUAL PREDITOR, LIFE TIME REGISTRATION WITH STATE
               POLICE; RESIDENCE, EMPLOYMENT, SCHOOL, PAY COURT COST & FINES, SENTENCE TO RUN
               CONSECUTIVE WITH ANY OTHER SENTENCE PRESENTLY SERVING
    2 / Aggravated Assault                                                    Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                        Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                  Dismissed - LOE                                 M2           18 § 5104
Proceed to Court
  Information Filed                                                          06/02/2011                                    Not Final
    1 / Criminal Attempt - Escape                                               Held for Court                                  F3           18 § 901 §§ A
    2 / Aggravated Assault                                                      Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                          Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault with intent to                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
    tickle
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam                                                             01/05/2012

 LINKED SENTENCES:
    Link 1
       CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Probation is Consecutive to
          CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Confinement
""",
r"""
Lower Court Proceeding (generic)
  Preliminary Hearing                                                        05/19/2011                                    Not Final
      1 / Manufacture, Delivery, or Possession With Intent to                   Held for Court                                  F            35 § 780-113 §§ A30
      Manufacture or Deliver
      2 / Criminal Conspiracy Engaging - Manufacture,                           Held for Court                                  F            18 § 903 §§ A1
      Delivery, or Possession With Intent to Manufacture or
      Deliver
      3 / Int Poss Contr Subst By Per Not Reg                                   Held for Court                                  M            35 § 780-113 §§ A16
""",
r"""Lower Court Proceeding (generic)
  Lower Court Disposition                                                    03/02/2011                                    Not Final
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                     Guilty                                          M            75 § 3802 §§ A1*
       Wright Padilla, Nina N.                                       01/02/2014
         Probation                                                       Max of 7.00 Years
                                                                         7 years
             FIR evaluation ordered from the street. Defendant must follow FIR recommendations
               To stay away from victim(s).
               Defendant to be supervised under the Mental Health Unit.
               Probationary fees waived
    99,999 / False Identification To Law Enforcement                            Not Guilty                                      M3           18 § 4914 §§ A
    Officer
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
Proceed to Court
  Information Filed                                                          06/02/2011                                    Not Final
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                          Added by Information                            M            75 § 3802 §§ A1*
      Replaced by 18 § 2701 §§ A3, Simple Assault
      2 / DUI: Controlled Substance - Impaired Ability - 1st                      Added by Information                            M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
   99,999 / False Identification To Law Enforcement                               Disposed at Lower Court                         M3           18 § 4914 §§ A
   Officer
Quashed
    Trial                                                                      10/28/2011                                     Final Disposition
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                            Quashed                                         M            75 § 3802 §§ A1*
      2 / DUI: Controlled Substance - Impaired Ability - 1st                      Quashed                                         M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
      99,999 / False Identification To Law Enforcement                            Disposed at Lower Court                         M3           18 § 4914 §§ A
      Officer
""",
r"""
Lower Court Proceeding (generic)
  Lower Court Disposition                                                    02/07/2011                                    Not Final
      99,999 / DUI: Controlled Substance - Impaired Ability -                   Guilty                                          M            75 § 3802 §§ D2*
      1st Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                     Guilty                                          M            75 § 3802 §§ A1*
Proceed to Court
  Information Filed                                                          06/02/2011                                    Not Final
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                          Added by Information                            M            75 § 3802 §§ A1*
      2 / DUI: Controlled Substance - Impaired Ability - 1st                    Added by Information                            M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Controlled Substance - Impaired Ability -                     Disposed at Lower Court                         M            75 § 3802 §§ D2*
      1st Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
Nolle Prossed
    Trial                                                                      12/06/2011                                     Final Disposition
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                            Nolle Prossed                                   M            75 § 3802 §§ A1*
      2 / DUI: Controlled Substance - Impaired Ability - 1st                      Nolle Prossed                                   M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Controlled Substance - Impaired Ability -                     Disposed at Lower Court                         M            75 § 3802 §§ D2*
      1st Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
"""
r"""
Lower Court Proceeding (generic)
  Lower Court Disposition                                                    02/07/2011                                    Not Final
      99,999 / DUI: Controlled Substance - Impaired Ability -                   Guilty                                          M            75 § 3802 §§ D2*
      Manufacture or Deliver
         Shreeves-Johns, Karen                                                     07/13/2011
            Probation and fun                                                                 Max of 3.00 Years                                   07/13/2011
                                                                                     3 years
                  Defendant is to pay imposed mandatory court costs.
                  To submit to random drug screens.
                  To pursue a prescribed secular course of study or vocational training.
                  Case relisted for status of compliance on 9/22/11 courtroom 605.
       Shreeves-Johns, Karen                                                     12/20/2011
          Confinement                                                              Min of 11.00 Months 15.00 Days                      12/20/2011
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                     Guilty                                          M            75 § 3802 §§ A1*
Proceed to Court
  Information Filed                                                          06/02/2011                                    Not Final
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                          Added by Information                            M            75 § 3802 §§ A1*
       ShreevesJohns, Karen                                                     07/13/2011
       Shreeves-Johns, Karen                                                     12/20/2011
      2 / DUI: Controlled Substance - Impaired Ability - 1st                    Added by Information                            M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Controlled Substance - Impaired Ability -                     Disposed at Lower Court                         M            75 § 3802 §§ D2*
      1st Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
Nolle Prossed
    Trial                                                                      12/06/2011                                     Final Disposition
      1 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                            Nolle Prossed                                   M            75 § 3802 §§ A1*
      2 / DUI: Controlled Substance - Impaired Ability - 1st                      Nolle Prossed                                   M            75 § 3802 §§ D2*
      Offense
      99,999 / DUI: Controlled Substance - Impaired Ability -                     Disposed at Lower Court                         M            75 § 3802 §§ D2*
      1st Offense
      99,999 / DUI: Gen Imp/Inc of Driving Safely - 1st Off                       Disposed at Lower Court                         M            75 § 3802 §§ A1*
""",
r"""    1 / Rape Forcible Compulsion                                              Guilty Plea - Negotiated                        F1           18 § 3121 §§ A1
       Hill, Glynnis                                                             05/17/2011
       Hill, Glynnis                                                             09/09/2011
         Confinement                                                               7 1/2 years to 15 years                             09/09/2011
               DEFENDANT FOUND NOT TO BE SEXUAL PREDITOR, LIFE TIME REGISTRATION WITH STATE
               POLICE; RESIDENCE, EMPLOYMENT, SCHOOL, PAY COURT COST & FINES, SENTENCE TO RUN
               CONSECUTIVE WITH ANY OTHER SENTENCE PRESENTLY SERVING
""",
r"""       Hill, Glynnis                                                             05/17/2011
""",
r"""
    2 / Aggravated Assault with intent to                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
    tickle
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
""",
r"""Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                   Sentence Conditions

Lower Court Proceeding (generic)
  Preliminary Hearing                                                        05/18/2011                                    Not Final
    1 / Criminal Attempt - Escape                                             Held for Court                                  F3           18 § 901 §§ A
    2 / Aggravated Assault                                                    Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                        Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                  Dismissed - LOE                                 M2           18 § 5104
Proceed to Court
  Information Filed                                                          06/02/2011                                    Not Final
    1 / Criminal Attempt - Escape                                               Held for Court                                  F3           18 § 901 §§ A
    2 / Aggravated Assault                                                      Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                          Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault with intent to                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
    tickle
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam                                                             01/05/2012

 LINKED SENTENCES:
    Link 1
       CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Probation is Consecutive to
          CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Confinement
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam
Proceed to Court
  Information Filed                                                          01/13/2011                                    Not Final
    1 / Ethnic Intimidation                                                     Held for Court                                  F1           18 § 2710 §§ A
    2 / Arson-Danger Of Death Or Bodily Inj                                     Held for Court                                  F1           18 § 3301 §§ A1I
    3 / Causing Catastrophe                                                     Held for Court                                  F1           18 § 3302 §§ A
    4 / Poss Instrument Of Crime W/Int                                          Held for Court                                  M1           18 § 907 §§ A
    5 / Terroristic Threats W/ Int To Terrorize Another                         Held for Court                                  M1           18 § 2706 §§ A1
    6 / Crim'l Misch-Tamper W/Property                                          Replacement by Information                      M2           18 § 3304 §§ A2
    7 / Recklessly Endangering Another Person                                   Held for Court                                  M2           18 § 2705
    8 / Harassment - Comm. Lewd, Threatening, Etc.                              Held for Court                                  M3           18 § 2709 §§ A4
    Language
    9 / Risking Catastrophe                                                     Added by Information                            F3           18 § 3302 §§ B
    99,999 / Criminal Mischief                                                  Charge Changed                                  M2           18 § 3304 §§ A4
     Replaced by 18 § 3304 §§ A2, Crim'l Misch-Tamper W/Property
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam
Proceed to Court
  Information Filed                                                          01/13/2011                                    Not Final
    1 / Ethnic Intimidation                                                     Held for Court                                  F1           18 § 2710 §§ A
    2 / Arson-Danger Of Death Or Bodily Inj                                     Held for Court                                  F1           18 § 3301 §§ A1I
    3 / Causing Catastrophe                                                     Held for Court                                  F1           18 § 3302 §§ A
    4 / Poss Instrument Of Crime W/Int                                          Held for Court                                  M1           18 § 907 §§ A
    5 / Terroristic Threats W/ Int To Terrorize Another                         Held for Court                                  M1           18 § 2706 §§ A1
    6 / Crim'l Misch-Tamper W/Property                                          Replacement by Information                      M2           18 § 3304 §§ A2
    7 / Recklessly Endangering Another Person                                   Held for Court                                  M2           18 § 2705
    8 / Harassment - Comm. Lewd, Threatening, Etc.                              Held for Court                                  M3           18 § 2709 §§ A4
    Language
    9 / Risking Catastrophe                                                     Added by Information                            F3           18 § 3302 §§ B
    99,999 / Criminal Mischief                                                  Charge Changed                                  M2           18 § 3304 §§ A4
     Replaced by 18 § 3304 §§ A2, Crim'l Misch-Tamper W/Property
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam
Proceed to Court
  Information Filed                                                          01/13/2011                                    Not Final
    1 / Ethnic Intimidation                                                     Held for Court                                  F1           18 § 2710 §§ A
    2 / Arson-Danger Of Death Or Bodily Inj                                     Held for Court                                  F1           18 § 3301 §§ A1I
    3 / Causing Catastrophe                                                     Held for Court                                  F1           18 § 3302 §§ A
    4 / Poss Instrument Of Crime W/Int                                          Held for Court                                  M1           18 § 907 §§ A
    5 / Terroristic Threats W/ Int To Terrorize Another                         Held for Court                                  M1           18 § 2706 §§ A1
    6 / Crim'l Misch-Tamper W/Property                                          Replacement by Information                      M2           18 § 3304 §§ A2
    7 / Recklessly Endangering Another Person                                   Held for Court                                  M2           18 § 2705
    8 / Harassment - Comm. Lewd, Threatening, Etc.                              Held for Court                                  M3           18 § 2709 §§ A4
    Language
    9 / Risking Catastrophe                                                     Added by Information                            F3           18 § 3302 §§ B
    99,999 / Criminal Mischief                                                  Charge Changed                                  M2           18 § 3304 §§ A4
     Replaced by 18 § 3304 §§ A2, Crim'l Misch-Tamper W/Property
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam                                                             01/05/2012
""",
r"""
Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
  Information Filed                                                          06/02/2011                                    Not Final
    1 / Criminal Attempt - Escape                                               Held for Court                                  F3           18 § 901 §§ A
    2 / Aggravated Assault                                                      Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                          Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam                                                             01/05/2012
""",
r"""Disposition
  Case Event                                                                 Disposition Date                              Final Disposition
    Sequence/Description                                                       Offense Disposition                             Grade       Section
          Sentencing Judge                                                       Sentence Date                                       Credit For Time Served
            Sentence/Diversion Program Type                                           Incarceration/Diversionary Period                 Start Date
                 Sentence Conditions
  Information Filed                                                          06/02/2011                                    Not Final
    1 / Criminal Attempt - Escape                                               Held for Court                                  F3           18 § 901 §§ A
    2 / Aggravated Assault                                                      Held for Court                                  F2           18 § 2702 §§ A
    3 / Simple Assault                                                          Held for Court                                  M2           18 § 2701 §§ A
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
Guilty Plea - Negotiated
  Trial                                                                      01/05/2012                                    Final Disposition
    1 / Criminal Attempt - Escape                                               Guilty Plea - Negotiated                        F3           18 § 901 §§ A
          Beloff, Adam                                                             01/05/2012
            No Further Penalty
    2 / Aggravated Assault                                                      Guilty Plea - Negotiated                        F2           18 § 2702 §§ A
          Beloff, Adam                                                             01/05/2012
            Confinement                                                              Min of 3.00 Months                                  01/05/2012
                                                                                     Max of 23.00 Months
                                                                                     3 - 23 months
            Probation                                                                Min of 1.00 Years
                                                                                     Max of 1.00 Years
                                                                                     1 year
    3 / Simple Assault                                                          Nolle Prossed                                   M2           18 § 2701 §§ A
          Beloff, Adam                                                             01/05/2012
    99,999 / Resist Arrest/Other Law Enforce                                    Disposed at Lower Court                         M2           18 § 5104
          Beloff, Adam                                                             01/05/2012

 LINKED SENTENCES:
    Link 1
       CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Probation is Consecutive to
          CP-51-CR-0005727-2011 - Seq. No. 2 (18§ 2702 §§ A) - Confinement
"""]


class DispositionVisitor(NodeVisitor):

  #Non-terminal methods
  def generic_visit(self, node, vc):
    return self.stringify(vc)

  def visit_section_disposition_sentencing_body(self, node, vc):
    contents = self.stringify(vc).replace("><", "> <")
    return " <disposition_sentencing_body> %s </disposition_sentencing_body> " % contents

  def visit_disposition_subsection(self, node, vc):
    contents = self.stringify(vc)
    return " <disposition_subsection> %s </disposition_subsection> " % contents

  def visit_disposition_type(self, node, vc):
    contents = self.stringify(vc)
    return " <disposition_type> %s </disposition_type> " % contents.strip()

  def visit_case_event(self, node, vc):
    contents = self.stringify(vc)
    return " <case_event> %s </case_event> " % contents

  def visit_case_event_desc(self, node, vc):
    contents = self.stringify(vc)
    return " <case_event_desc> %s </case_event_desc> " % contents

  def visit_code_section(self, node, vc):
    contents = self.stringify(vc)
    return " <code_section> %s </code_section> " % contents

  def visit_case_event_desc_and_date(self, node, vc):
    contents = self.stringify(vc)
    return " <case_event_desc_and_date> %s </case_event_desc_and_date> " % contents

  def visit_case_event_line(self, node, vc):
    contents = self.stringify(vc)
    return " <case_event_type> %s </case_event_type> " % contents

  def visit_date(self, node, vc):
    contents = self.stringify(vc)
    return " <date> %s </date> " % contents

  def visit_is_final(self, node, vc):
    contents = self.stringify(vc)
    return " <finality> %s </finality> " % contents

  def visit_sequence(self, node, vc):
    contents = self.stringify(vc)
    contents = contents.replace(" / ", " ")
    return " <sequence> %s </sequence> " % contents

  def visit_sequence_description(self, node, vc):
    contents = self.stringify(vc)
    return " <sequence_description> %s </sequence_description> " % contents

  def visit_sequence_description_continued(self, node, vc):
    contents = self.stringify(vc)
    return " <sequence_description_continued> %s </sequence_description_continued> " % contents.strip()

  def visit_sequence_number(self, node, vc):
    contents = self.stringify(vc)
    return " <sequence_num> %s </sequence_num> " % contents

#   Regular version
  def visit_things_a_judge_did(self, node, vc):
    contents = self.stringify(vc)
    return " <judge_action> %s </judge_action> " % contents

  #Regular version
#   def visit_sentence_info(self, node, vc):
#     contents = self.stringify(vc)
#     return " <sentence_info> %s </sentence_info> " % contents

  #   Version for identifying sentence maxes and mins
  def visit_sentence_info(self, node, vc):
    print("visit_sentence_info")
    min_pattern = re.compile(r".* min of (?P<time>[0-9\./]*) (?P<units>\w+).*", flags=re.IGNORECASE|re.DOTALL)
    max_pattern = re.compile(r".* max of (?P<time>[0-9\./]*) (?P<units>\w+).*", flags=re.IGNORECASE|re.DOTALL)
    range_pattern = re.compile(r".*?(?P<min_time>(?:[0-9\.\/]+(?:\s|$))+)(?P<min_unit>\w+ )?(?:to|-) (?P<max_time>(?:[0-9\.\/]+(?:\s|$))+)(?P<max_unit>\w+).*", flags=re.IGNORECASE|re.DOTALL)
    single_term_pattern = re.compile(r".* \s{5,}(?P<time>[0-9\./]+)\s(?P<unit>\w+)$.*", flags=re.IGNORECASE|re.DOTALL)
    temp_string = node.text
    print(temp_string)
    min_length = re.match(min_pattern, node.text)
    max_length = re.match(max_pattern, node.text)
    range = re.match(range_pattern, node.text)
    single_term = re.match(single_term_pattern, node.text)

    if min_length is not None:
      print("Min-length is %s number of %s" % (min_length.group('time'), min_length.group('units')))
      min_length = "<min_length> <time> %s </time> <unit> %s </unit> </min_length>" % (min_length.group('time'),min_length.group('units'))
    else:
      print("Min length not found.")

    if max_length is not None:
      print("Max-length is %s number of %s" % (max_length.group('time'), max_length.group('units')))
      max_length = "<max_length> <time> %s </time> <unit> %s </unit> </max_length>" % (max_length.group('time'),max_length.group('units'))
    else:
      print("Max length not found")

    if range is not None:
      print(range.groups())
      print("Range from %s to %s %s" % (range.group('min_time'), range.group('max_time'),range.group('max_unit')))
      if range.group('min_unit') is not None:
        min_length = "<min_length> <time> %s </time> <unit> %s </unit> </min_length>" % (range.group('min_time'), range.group('min_unit'))
      else:
        min_length = "<min_length> <time> %s </time> <unit> %s </unit> </min_length>" % (range.group('min_time'), range.group('max_unit'))
      max_length = "<max_length> <time> %s </time> <unit> %s </unit> </max_length>" % (range.group('max_time'),range.group('max_unit'))
    else:
      print("Range not found.")

    if single_term is not None:
      print("Single term is %s %s" % (single_term.group('time'), single_term.group('unit')))
      min_length = "<min_length> <time> %s </time> <unit> %s </unit> </min_length>" % (single_term.group('time'), single_term.group('unit'))
      max_length = "<max_length> <time> %s </time> <unit> %s </unit> </max_length>" % (single_term.group('time'), single_term.group('unit'))
    else:
      print("Single terms not found.")

    contents = self.stringify(vc)
    if min_length is not None and max_length is not None:
      print(re.sub(r"<length_of_sentence>(.*)</length_of_sentence>", min_length + max_length, contents))
    print("Finished with visit_sentence_info.")
    return " <sentence_info> %s </sentence_info> " % contents


  def visit_judge_name(self, node, vc):
    contents = self.stringify(vc)
    return " <judge_name> %s </judge_name> " % contents

  def visit_offense_disposition(self, node, vc):
    contents = self.stringify(vc)
    return " <offense_disposition> %s </offense_disposition> " % contents

  def visit_sentence_program_info(self, node, vc):
    contents = self.stringify(vc)
    return " <sentence_program_information> %s </sentence_program_information> " % contents

  def visit_program(self, node, vc):
    contents = self.stringify(vc)
    return " <program> %s </program> " % contents

  def visit_length_of_sentence(self, node, vc):
    contents = self.stringify(vc)
    return " <length_of_sentence> %s </length_of_sentence> " % contents

  def visit_extra_sentence_details(self, node, vc):
    contents = self.stringify(vc).replace("\n","...")
    return " <extra_sentence_details> %s </extra_sentence_details> " % contents

  def visit_footer(self, node, vc):
    contents = self.stringify(vc)
    return " <footer> %s </footer> " % contents

  #Terminal methods
  def visit_grade(self, node, vc):
    return " <grade> %s </grade> " % node.text

  def visit_single_char_no_comma_or_ws(self, node, vc):
    return node.text

  def visit_single_content_char_no_ws(self, node, vc):
    return node.text

  def visit_single_content_char(self, node, vc):
    return node.text

  def visit_single_content_char_no_comma(self, node, vc):
    return node.text

  def visit_number(self, node, vc):
    return node.text

  def visit_forward_slash(self, node, vc):
    return node.text

  def visit_new_line(self, node, vc):
    return node.text

  def visit_ws(self, node, vc):
    return node.text

  def visit_comma(self, node, vc):
    return node.text

  #Helpers
  def stringify(self, content):
    return "".join(content)





text = texts[0]
grammar = Grammar(grammars[0])

print("Text type: %s" % type(text))
# print("-----")
# print(text)
# print("-----")
root = grammar.parse(text)
visitor = DispositionVisitor()
parsed_text = visitor.visit(root)
parser = etree.XMLParser(remove_blank_text=True)
file_object = io.StringIO(parsed_text.strip().replace("&","&amp;"))
section_root = etree.parse(file_object, parser).getroot()

with open("disposition_output.xml", "w+") as f:

  f.write(etree.tounicode(section_root, pretty_print=True))

f.close()
print("Successfully parsed.")