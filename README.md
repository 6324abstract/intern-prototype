## Development

### Set up environment and install dependencies

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -U pip wheel setuptools
pip install pip-tools
pip-sync requirements-dev.txt
pre-commit install
```

### Run checks

```bash
# Pre-commit hooks
pre-commit run --all-files
# Mypy types check
mypy --show-error-codes cwdb tts
```

### Run tests
```bash
pytest
```

### Update requirements

The `.txt` requirement files are build from `.in` files.

```bash
./tools/rebuild-requirements.sh
```
