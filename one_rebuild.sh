cd auto-client1

poetry build -f wheel -o ../dist/

cd ..

uv add dist/auto_client1-1.0.0-py3-none-any.whl

uv lock 

uv sync --all-groups