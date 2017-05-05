# yǔfǎ 语法 grammar 

_This is still beta software_. As such you should assume that the schema can and will change.

## introduction

_yufa_ is my [latest](https://github.com/parryc/tungumal) [attempt](https://github.com/parryc/aistritheoir) to try to make a more human-readable natural language grammar description framework. I say _more_ human-readable cause [GrammaticalFramework](http://www.grammaticalframework.org/) is technically human readable. It is also driven by my desire to codeify the rules to conjugation and declension as I learn them and have a method of validating that I have in fact learned the rules correctly.

## how to design a grammar

TODO :)

## how to run

### visual model

_yufa_ uses [textX](http://igordejanovic.net/textX/) to parse the description language. It also has some great visualization tools, with the help of [graphviz](http://www.graphviz.org/) (which provides the _dot_ program).

```
>>> from textx.export import model_export
>>> meta  = metamodel_from_file('Rules.tx')
>>> model = meta.model_from_file('{path to ruleset}')
>>> model_export(model, 'program.dot')
$ dot -Tpng program.dot -O program.dot.png
```

### command line

`python parser.py {language} {word} {pronoun} {ruleset} {conjugation_group}[optional]`

For example:

* `python parser.py dutch nemen 1sg prs` will result in `neem`.
* `python parser.py lithuanian dirba 1sg prs A` will result in `dirbu`. The `A` indicates that the verb _dirbti_ (seen there in the 3 person present form) is an _A_ class verb.
* `python parser.py russian работать 1sg prs` will result in `работаю`.

### testing

Tests with nose: `python -m nose2`

