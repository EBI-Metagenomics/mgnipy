jupytext openapi-py-client/*.ipynb --sync
jupytext tutorial/*.ipynb --sync

sphinx-apidoc --force --separate \
    --implicit-namespaces --module-first \
    -o reference/mgnipy ../mgnipy

# sphinx-apidoc --force \
#     --implicit-namespaces --module-first \
#     -o reference/mgni-py-v1 ../openapi/mgni-py-v1/mgni_py_v1

# sphinx-apidoc --force \
#     --implicit-namespaces --module-first \
#     -o reference/mgni-py-v2 ../openapi/mgni-py-v2/mgni_py_v2

# check index.md and conf.py files
sphinx-build -n -W --keep-going -b html ./ ./_build/