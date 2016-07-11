#!/usr/bin/env python
# coding: utf-8
from textx.metamodel import metamodel_from_file
import re
import sys

class Parser(object):

  def __init__(self, word, conjugation):
    self.context = word
    self.base    = word
    self.state   = ''
    self.status  = ''
    self.conjugation = conjugation

    self.orthography = {
      'C' : 'bcdfghjklmnpqrstvwxyz'
     ,'V' : 'aeiou'
    }


  def __str__(self):
    return '{} is now {} [{}, {}]'.format(self.base, self.context, self.state, self.status)

  def parse(self, model):
    self.state = model.name
    for step in model.steps:
      self._run(step)

    for conjugation in model.conjugations:
      if conjugation.type[0] == self.conjugation:
        if conjugation.conjugation[0] == 'base':
          self.context = self.base
        else:
          addition = ''.join(conjugation.conjugation[0].string)
          self.context = self.context + addition

    print('present: {}'.format(self))


  def name(self, command):
    return command.__class__.__name__

  def parse_set(self, step):
    if step.action == 'otherwise' and not self.status:
      self.status = step.status
    elif self.name(step.action) == 'EndsWith':
      regex = self.action_regex(step.action)
      if regex.search(self.context):
        self.status = step.status

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
    else:
      regex = self.what_regex(action.what)
    return re.compile(regex)

  def what_regex(self, whats):
    regex = ''
    for what in whats:
      if self.name(what) == 'Quantity':
        quantitize = '\\1' * (what.amount - 1)
        regex += '([{}]){}'.format(self.orthography[what.type],quantitize)
      else:
        regex += ''.join(self._expand(what.string))
    return regex

  def _last_replace(self, s, replace, replace_with):
    matches = re.finditer(replace, s)
    if matches:
      # Find last match
      for m in matches:
        match = m
      start = s[:match.start(0)]
      end   = s[match.end(0):]
      return start + replace_with + end
    else:
      return s

  def _last_double(self, s, replace):
    matches = re.finditer(replace, s)
    if matches:
      # Find last match
      for m in matches:
        match = m
      text  = match.group(0)
      start = s[:match.start(0)]
      end   = s[match.end(0):]
      return start + text + text + end
    else:
      return s


  def _expand(self, string):
    string = ''.join(string)
    if string in self.orthography:
      return '[{}]'.format(self.orthography[string])
    else:
      return string

  def _run(self, command):
    getattr(self, 'parse_'+self.name(command).lower())(command)

def main():
  # python parser.py [word]
  meta                = metamodel_from_file('Rules.tx')
  dutch_present_tense = meta.model_from_file(sys.argv[1])
  Parser(sys.argv[2], sys.argv[3]).parse(dutch_present_tense)


if __name__ == "__main__":
    main()