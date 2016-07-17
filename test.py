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
def test_from_function(file, base, conjugation, form, expected, *args):
  meta  = metamodel_from_file('Rules.tx')
  form  = file.replace('tests.yufa',form + '.tx')
  ortho = file.replace('tests.yufa','orthography.tx')
  model = meta.model_from_file(form)

  p = Parser(base, '', os.path.join(ortho))
  p.parse(model, conjugation)

  parsed = p.context
  assert expected == parsed