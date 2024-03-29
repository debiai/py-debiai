# Testing requirements

- pytest
- pytest-cov

# Running tests:

> pytest -sx --cov-report term --cov=debiai --cov-report=html tests/

Coverage will be available at: **_htmlcov/index.html_**

> firefox htmlcov/index.html
