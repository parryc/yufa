from textx.export import model_export
dot -Tpng program.dot -O program.dot.png
model_export(mm, 'program.dot')

python parser.py dutch/prs.tx spelen 3pl
