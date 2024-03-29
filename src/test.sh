set -ex
pip uninstall testaaaaa -y || true
pip uninstall testbbbbb -y || true
pip uninstall torch -y || true

pip install http://127.0.0.1:8000/targz/testaaaaa/1
pip install http://127.0.0.1:8000/targz/testbbbbb/2

pip install "torch>=2" -i http://127.0.0.1:8000 # require a registered pypi package
