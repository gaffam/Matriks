.PHONY: setup test run-api package

setup:
./setup.sh

test:
python -m pytest --cov=src tests/

run-api:
uvicorn src.api_server:app --reload

package:
./create_package.sh proai_package.tar.gz
