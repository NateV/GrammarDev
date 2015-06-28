from grammar_dev.grammars import case_info_grammar as cig
from io import StringIO
from lxml import etree
from glob import iglob

def test_parse_one():
  file = "tests/Example_Case_Information.txt"
  #"./texts/Case_Info_Samples/CP-51-CR-0000001-2011_Case_Information.txt"
  with open(file, "r") as f:
    text = f.read()
  f.close()
  parsed_xml = cig.parse(text)
  root = etree.parse(StringIO(parsed_xml)).getroot()
  assert root.xpath("/case_info/judge_assigned/text()")[0] == " Smith, John "

def test_parse_many():
  number_processed = 0
  number_failures = 0
  failures = []
  iterator = iglob("./texts/Case_Info_Samples/*.txt")
  for section_file in iterator:
    print("Processing {}".format(section_file))
    with open(section_file, "r") as sf:
      text = sf.read().strip()
    sf.close()
    number_processed += 1
    try:
      xml = cig.parse(text)
      judge_name = etree.parse(StringIO(xml)).getroot().xpath("/case_info/judge_assigned/text()")[0]
      print("Judge Assigned: {}".format(judge_name))
      assert len(judge_name) > 0
    except:
      number_failures += 1
      failures.append(section_file)

  assert number_failures == 0
  print("Num processed: {}".format(number_processed))
  print("Num failures: {}".format(number_failures))
  print("Failures:")
  for failure in failures:
    print("    {}".format(failure))
  print("Done.")