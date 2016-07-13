from nose_parameterized import parameterized, param
from textx.metamodel import metamodel_from_file
import nose2
import os
from yufa.parser import Parser
from yufa.loader import Loader

def load_test_cases():
  pwd    = os.path.dirname(os.path.realpath(__file__))
  loader = Loader(pwd)
  return loader.generate_tests()

@parameterized(load_test_cases)
def test_from_function(base, conjugation, form, expected):
  pwd   = os.path.dirname(os.path.realpath(__file__))
  meta  = metamodel_from_file('Rules.tx')
  model = meta.model_from_file(os.path.join(pwd,form+'.tx'))

  p = Parser(base, '', os.path.join(pwd,'orthography.tx'))
  p.parse(model, conjugation)

  parsed = p.context
  assert expected == parsed