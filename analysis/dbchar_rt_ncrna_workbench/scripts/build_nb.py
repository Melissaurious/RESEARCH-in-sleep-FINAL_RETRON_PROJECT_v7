from pathlib import Path
import nbformat as nbf, sys
HERE = Path(__file__).resolve().parent
exec(open(HERE / "build_nb_part1.py").read())
for part in ["part1b","part2","part2b","part3","part4","part4b","part4c","part5f","part5","part6","part7","part8","part9"]:
    exec(open(HERE / f"build_nb_{part}.py").read())
nb = nbf.v4.new_notebook(cells=C)
nb.metadata["kernelspec"] = {"display_name": "dbchar-workbench", "language": "python", "name": "dbchar-workbench"}
nb.metadata["language_info"] = {"name": "python", "version": "3.12"}
out = sys.argv[1]
nbf.write(nb, out)
print("wrote", out, len(C), "cells")
