import os
from lxml import etree
from glob import iglob

def collect_section_samples(section, source, destination, number = float("inf")):
  """
  In:
    section: The name of a section to collect samples of
    source: The path to a directory of parsed dockets
    destination: The path to a directory where the new samples should go
    number: The number of samples to collect. Defaults to "as many as possible."
  """
  if not os.path.exists(destination):
    os.makedirs(destination)
  iterator = iglob("{}*.xml".format(source))
  counter = 0
  for file in iterator:
    if counter >= number:
      return
    tree = etree.parse(file)
    text = tree.xpath("//section[@name='{}']/text()".format(section))
    assert len(text) == 1
    text = text[0]
    docket_num = os.path.split(file)[1]
    docket_num = docket_num.replace("_","").replace("stitched","").replace("complete","").replace(".xml","")
    with open("{}{}_{}.txt".format(destination, docket_num, section), "w") as new_file:
      new_file.write(text)
      print("Wrote {}".format(new_file))
    new_file.close()

