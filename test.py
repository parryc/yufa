from nose_parameterized import parameterized, param
from textx.metamodel import metamodel_from_file
import nose2
import os
from parser import Parser
from loader import Loader

def load_test_cases():
  pwd    = os.path.dirname(os.path.realpath(__file__))
  loader = Loader(pwd)
  return loader.generate_tests()

def additional_args(args, pos):
  try:
    temp = args[pos]
    return args[pos]
  except Exception:
    return 'default'

def set_suffixes(args):
  """
    Set suffixes if they begin with a +
  """
  return [arg[1:] for arg in args if arg[0] == '+']

@parameterized(load_test_cases)
def test_from_function(file, language, base_word, form, inflection_type, expected, *args):
  """
    Additional args:
    0 = inflection group
  """
  p = Parser(language)

  inflection_group = additional_args(args, 0)
  suffixes = set_suffixes(args)

  p.setup(base_word, inflection_group)
  p.set_context(inflection_type)
  p.inflect(form)

  if suffixes:
    for suffix in suffixes:
      p.suffix(suffix)


  parsed   = p.context
  expected = ' '.join(expected)
  assert expected == parsed