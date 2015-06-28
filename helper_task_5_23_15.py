from helper import collect_section_samples
import os
import shutil
from glob import glob


def test_collect_section_samples():
  section = "Case_Information"
  source = "./texts/completely_parsed/"
  destination = "./texts/Case_Info_Samples/"
  number = 1

  if os.path.exists(destination):
    shutil.rmtree(destination)
  assert not os.path.exists(destination)

  collect_section_samples(section, source, destination, number)
  assert os.path.exists(destination)
  assert len(glob("{}*.txt".format(destination)))
