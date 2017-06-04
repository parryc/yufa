#!/usr/bin/env python
# coding: utf-8
import sys
from parser import Parser

def main():
  # python table.py [language base inflection_group additional1 additional2]
  def additional_args(args, pos):
    try:
      temp = args[pos]
      return args[pos]
    except Exception:
      return 'default'

  def print_row(col_1, col_2, size):
    return '{}| {}'.format(col_1.ljust(size, ' '), col_2.ljust(size, ' '))

  p = Parser(sys.argv[1])

  inflection_group = additional_args(sys.argv, 4)

  p.setup(sys.argv[2], inflection_group)
  p.set_context(sys.argv[3])

  singular_pronouns  = ['1sg', '2sg', '3sg']
  singular_inflected = [p.inflect(_p) for _p in singular_pronouns]
  plural_pronouns    = ['1pl', '2pl', '3pl']
  plural_inflected   = [p.inflect(_p) for _p in plural_pronouns]

  sg_max = len(max(singular_inflected, key=len))
  pl_max = len(max(plural_inflected, key=len))
  size   = max(sg_max, pl_max)

  header  = print_row('sg', 'pl', size)
  divider = '{}|{}'.format('-'.ljust(size, '-'), '-'.ljust(size, '-'))
  table   = [header, divider]
  for idx, val in enumerate(singular_inflected):
    table.append(print_row(val, plural_inflected[idx], size))

  print('\n'.join(table))

if __name__ == "__main__":
    main()