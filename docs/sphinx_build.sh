jupytext dev/*.ipynb --sync

jupytext tutorials/getting-started/available-resources.ipynb --sync
jupytext tutorials/getting-started/mgnify-biomes.ipynb --sync
jupytext tutorials/getting-started/study-analyses-simple.ipynb --sync

#jupytext tutorials/demos/get_all_analyses_for_study.ipynb --sync

sphinx-apidoc --force \
    --module-first  --remove-old -t _templates \
    -o reference ../mgnipy

# sphinx-apidoc --force \
#     --implicit-namespaces --module-first \
#     -o reference/emgapi-v2-client ../openapi/emgapi-v2-client/emgapi_v2_client

# check index.md and conf.py files
sphinx-build -n -W --keep-going -b html ./ ./_build/
