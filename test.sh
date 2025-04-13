set -ex
pip uninstall testaaaaa -y || true
pip uninstall testbbbbb -y || true
pip uninstall testccccc -y || true
pip uninstall torch -y || true

pip install http://127.0.0.1:8000/targz/testaaaaa/1
pip install http://127.0.0.1:8000/targz/testbbbbb/2
pip install http://127.0.0.1:8000//whl/testccccc/3/testccccc-3-py3-none-any.whl

pip install "torch>=2" -i http://127.0.0.1:8000 # require a registered pypi package
