#!/usr/bin/env python
# coding: utf-8
from textx.metamodel import metamodel_from_file
import re
import sys
import os

class Parser(object):

  def __init__(self, language):
    self.context    = ''
    self.base       = ''
    self.state      = ''
    self.group      = ''
    self.language   = language
    self.status     = {'default': ''}
    self.exceptions = {} 

    ortho_meta  = metamodel_from_file('Orthography.tx')
    orthography = ortho_meta.model_from_file(os.path.join(self.language, 'orthography.tx'))

    self.orthography = {}

    for token in orthography.tokens:
      self.orthography[''.join(token.token)] = ''.join(token.value)
    
  def __str__(self):
    return '{} is now {} [{}, {}] group={}'.format(self.base, self.context, self.state, self.status, self.group)

  def setup(self, word, inflection_group='default', **attributes):
    self.context = word
    self.base    = word
    self.state   = ''
    self.status  = {'default': ''}
    self.group   = inflection_group

    for key, value in attributes:
      self.extra[key] = value

  def set_context(self, inflection_type):
    meta  = metamodel_from_file('Rules.tx')
    model = meta.model_from_file(os.path.join(self.language, inflection_type + '.tx'))
    self.model = model
    self.state = model.name
    self.inflection_type = inflection_type

    for exception in self.model.exceptions:
      forms = {}
      for e in exception.exceptions:
        for t in e.type:
          forms[t] = e.override
      self.exceptions[exception.base_word] = forms

    for step in model.steps:
      if step == 'none':
        continue
      self._run(step)

  def inflect(self, form, reset=True):
    # Not resetting the parser will preserve the context between
    # calls of inflect
    if reset:
      self.context = self.base
      self.set_context(self.inflection_type)

    inflections = self.model.inflections

    if self.base in self.exceptions:
      exception = self.exceptions[self.base][form]
      if exception == 'base':
        self.context = self.base
      else:
        self.context = self.exceptions[self.base][form]
      return #End if there is an exception

    # If the inflectional form has different groups
    # set the list of inflections to be the group
    # that matches
    for _group in self.model.inflection_groups:
      if _group.group[0] == self.group:
        inflections = _group.inflections

    for inflection in inflections:
      if form in inflection.type:
        inflection_parts = inflection.inflection_parts

        # If there is an individual exception for one
        # of the inflections
        if inflection.exception:
          ex = inflection.exception
          if self._get_status(ex.attribute) == ex.value:
            inflection_parts = ex.alternative

        for inf in inflection_parts:
          if inf == 'base':
            self.context = self.base
          elif inf == 'nothing':
            continue
          elif self.name(inf) == 'Minus':
            subtraction = r'{}$'.format(inf.string)
            self.context = re.sub(subtraction, '', self.context)
          elif self.name(inf) == 'Preword':
            self.context = inf.string + ' ' + self.context
          elif self.name(inf) == 'Prefix':
            self.context = inf.string + self.context
          else:
            addition = ''.join(inf.string)
            self.context = self.context + addition

    return self.context

  def suffix(self, suffix):
    suffixes = self.model.suffixes
    for _suffix in suffixes:
      if _suffix.suffix[0] == suffix:
        suffix_steps = _suffix.steps

    for step in suffix_steps:
      if step == 'none':
        continue
      self._run(step)

    return self.context

  def name(self, command):
    return command.__class__.__name__

  def parse_set(self, step):
    if self.name(step.action) == 'Otherwise' and not self.status:
      self._set_status(step.status)
    elif self.name(step.action) in ['EndsWith', 'Is']:
      regex = self.action_regex(step.action)
      if regex.search(self.context):
        # If we're setting a specific attribute, rather than
        # the generic catch all 'status' attribute
        if step.value:
          self._set_status(step.value, step.status)
        else:
          self._set_status(step.status)

  def parse_add(self, step):
    self.context += self._stringify(step.what)[0]

  def parse_remove(self, step):
    regex = re.compile(self.what_regex(step.what))
    if self.name(step.what[0]) == 'Last':
      self.context = self._last_replace(self.context, regex, '')
    else:
      self.context = regex.sub('',self.context)

  def parse_change(self, step):
    regex = re.compile(self.what_regex(step.what))
    if self.name(step.what[0]) == 'Last':
      self.context = self._last_replace(self.context, regex, step.to)
    else:
      self.context = regex.sub(step.to,self.context)

  def parse_double(self, step):
    regex = '({})'.format(self.what_regex(step.what))
    regex = re.compile(regex)
    if self.name(step.what[0]) == 'Last':
      self.context = self._last_double(self.context, regex)
    else:
      self.context = regex.sub(r'\1\1',self.context)

  def parse_if(self, step):
    """
      Parse an if statement.

      if {step.condition} then ==> check against the default status.
      if {step.condition} is {step.vaue} then ==> check if the status[condition] is the value
      if 'group' is {step.value} then ==> check if the group is set to step.value
    """
    if self._get_status() == step.condition or\
       self._get_status(step.condition) == step.value or\
       (step.condition == 'group' and self.group == step.value):
      self._run(step.action)
    elif step.otherwise:
      self._run(step.otherwise)

  def action_regex(self, action):
    regex = ''

    if self.name(action) == 'EndsWith':
      regex = '{}$'.format(self.what_regex(action.what))
    elif self.name(action) == 'Is':
      regex = '^{}$'.format(self.what_regex(action.what))
    else:
      regex = self.what_regex(action.what)
    return re.compile(regex)

  def what_regex(self, whats):
    regex = ''
    for what in whats:
      name   = self.name(what)
      if name not in ['Quantity']:
        string = self._stringify(what.string)

      if self.name(what) == 'Quantity':
        quantitize = '\\1' * (what.amount - 1)
        regex += '([{}]){}'.format(self.orthography[what.type],quantitize)
      elif name == 'Or':
        regex += '({})?'.format(self._expand(string))
      else:        
        regex += ''.join(self._expand(string))
    return regex

  def _last_replace(self, s, replace, replace_with):
    matches = re.finditer(replace, s)
    match   = None
    # Find last match
    for m in matches:
      match = m

    if match:
      start = s[:match.start(0)]
      end   = s[match.end(0):]
      return start + replace_with + end
    else:
      return s

  def _last_double(self, s, replace):
    matches = re.finditer(replace, s)
    match   = None
    # Find last match
    for m in matches:
      match = m

    if match:
      text  = match.group(0)
      start = s[:match.start(0)]
      end   = s[match.end(0):]
      return start + text + text + end
    else:
      return s

  def _expand(self, string):
    if string in self.orthography:
      return '[{}]'.format(self.orthography[string])
    else:
      return string

  def _stringify(self, string):
    if isinstance(string[0], str):
      return string[0]
    else:
      return string[0].string

  def _set_status(self, value, key='default'):
    if key == 'group':
      self.group = value
    else:
      self.status[key] = value

  def _get_status(self, key='default'):
    try:
      return self.status[key]
    except Exception:
      return None

  def _run(self, command):
    getattr(self, 'parse_'+self.name(command).lower())(command)

def main():
  # python parser.py [language base form inflection_group additional1 additional2]
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
    if len(args) > 5:
      return [arg[1:] for arg in args if arg[0] == '+']

  p = Parser(sys.argv[1])
  suffixes = set_suffixes(sys.argv)
  inflection_group = additional_args(sys.argv, 5)

  p.setup(sys.argv[2], inflection_group)
  p.set_context(sys.argv[4])
  p.inflect(sys.argv[3])

  if suffixes:
    for suffix in suffixes:
      p.suffix(suffix)

  print(p)

if __name__ == "__main__":
    main()