# Technical Test Template

## Getting started

We have set up a basic Flask API that runs on port `5000` and included a `pytest` test showing the endpoint working.

If you prefer to use FastAPI, Django or other Python packages, feel free to add any you want using Poetry.
We have included a `Makefile` for conveince but you are free to run the project however you want.

### Requirements

- Python 3.12
- [Poetry](https://python-poetry.org/docs/) for dependency management

### Install dependencies

```sh
poetry install
```

### Start API server

```sh
make run
```

### Run tests

```sh
make test
```

## Testing

```sh
curl -XPOST 'http://127.0.0.1:5000/event' -H 'Content-Type: application/json' \
-d '{"type": "deposit", "amount": "42.00", "user_id": 1, "time": 0}'
```
