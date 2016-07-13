#!/usr/bin/env python
# coding: utf-8
from textx.metamodel import metamodel_from_file
import os

class Loader(object):
  def __init__(self, pwd):
    self.pwd  = pwd
    self.file = os.path.join 

  def generate_tests(self):
    meta  = metamodel_from_file('Tests.tx')
    model = meta.model_from_file(self.file(self.pwd,'tests.yufa'))

    tests = []

    for test in model.tests:
      tests.append((test.base, test.conjugation, test.form, test.expected) + tuple(test.extra))

    return tests
