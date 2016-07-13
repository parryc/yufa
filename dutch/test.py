from nose_parameterized import parameterized, param
from textx.metamodel import metamodel_from_file
import nose2
import os
from yufa.parser import Parser

def load_test_cases():
  return [
    ('spelen', 'speel', '1sg', 'prs'),
    ('spellen', 'spel', '1sg', 'prs'),
  ]

@parameterized(load_test_cases)
def test_from_function(base, expected, conjugation, ruleset):
  pwd   = os.path.dirname(os.path.realpath(__file__))
  meta  = metamodel_from_file('Rules.tx')
  model = meta.model_from_file(os.path.join(pwd,ruleset+'.tx'))

  p = Parser(base, '', os.path.join(pwd,'orthography.tx'))
  p.parse(model, conjugation)

  parsed = p.context
  assert expected == parsed