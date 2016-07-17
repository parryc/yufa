#!/usr/bin/env python
# coding: utf-8
from textx.metamodel import metamodel_from_file
import os
import glob

class Loader(object):
  def __init__(self, pwd):
    self.pwd  = pwd
    self.file = os.path.join 

  def generate_tests(self):
    meta  = metamodel_from_file('Tests.tx')
    files = self.search_for_yufa_files()
    tests = []

    for file in files:
      model = meta.model_from_file(file)

      for test in model.tests:
        tests.append((file, test.base, test.conjugation, test.form, test.expected) + tuple(test.extra))

    return tests

  def search_for_yufa_files(self):
    file_list = []
    for root, dirs, files in os.walk("."):
      for file in files:
          if file.endswith(".yufa"):
               file_list.append(os.path.join(root, file))
    return file_list

