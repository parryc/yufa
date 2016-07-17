#!/usr/bin/env python
# coding: utf-8
from textx.metamodel import metamodel_from_file
import re
import sys
import os

class Parser(object):

  def __init__(self, language):
    self.context  = ''
    self.base     = ''
    self.state    = ''
    self.group    = ''
    self.language = language
    self.status   = {'default': ''}

    ortho_meta  = metamodel_from_file('Orthography.tx')
    orthography = ortho_meta.model_from_file(os.path.join(self.language, 'orthography.tx'))

    self.orthography = {}

    for token in orthography.tokens:
      self.orthography[''.join(token.token)] = ''.join(token.value)
    
  def __str__(self):
    return '{} is now {} [{}, {}]'.format(self.base, self.context, self.state, self.status)

  def setup(self, word, inflection_group=None, **attributes):
    self.context = word
    self.base    = word
    self.state   = ''
    self.status  = {'default': ''}
    self.group   = inflection_group

    for key, value in attributes:
      self.extra[key] = value

  def set_context(self, inflection_type):
    meta  = metamodel_from_file('Rules.tx')
    model = meta.model_from_file(os.path.join(self.language,inflection_type + '.tx'))
    self.model = model
    self.state = model.name
    for step in model.steps:
      self._run(step)

  def inflect(self, form):
    inflections = self.model.inflections

    # If the inflectional form has different groups
    # set the list of inflections to be the group
    # that matches
    for _group in self.model.inflection_groups:
      if _group.group[0] is self.group:
        inflections = _group.inflections

    for inflection in inflections:
      if inflection.type[0] == form:
        for inf in inflection.inflection:
          if inf == 'base':
            self.context = self.base
          else:
            addition = ''.join(inf.string)
            self.context = self.context + addition

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

  def parse_remove(self, step):
    regex = re.compile(self.what_regex(step.what))
    if self.name(step.what[0]) == 'Last':
      self.context = self._last_replace(self.context, regex, '')
    else:
      self.context = regex.sub('',self.context)

  def parse_double(self, step):
    regex = '({})'.format(self.what_regex(step.what))
    regex = re.compile(regex)
    if self.name(step.what[0]) == 'Last':
      self.context = self._last_double(self.context, regex)
    else:
      self.context = regex.sub(r'\1\1',self.context)

  def parse_if(self, step):
    if self.status == step.condition:
      self._run(step.action)

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
      string = self._stringify(what.string)

      if name == 'Or':
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
    self.status[key] = value

  def _get_status(self, key='default'):
    return self.status[key]

  def _run(self, command):
    getattr(self, 'parse_'+self.name(command).lower())(command)

def main():
  # python parser.py [language base form inflection_group additional1 additional2]
  def additional_args(args, pos):
    try:
      temp = args[pos]
      return args[pos]
    except Exception:
      return None

  p = Parser(sys.argv[1])

  inflection_group = additional_args(sys.argv, 5)

  p.setup(sys.argv[2], inflection_group)
  p.set_context(sys.argv[4])
  p.inflect(sys.argv[3])

  print(p)

if __name__ == "__main__":
    main()