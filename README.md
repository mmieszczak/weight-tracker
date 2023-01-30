# LTS Python programming workshop

The goal of this exercise is to build a simple web application.
Application is a weight tracker,
which allows the user to log their progress
and display historical data.

## Environment setup

### Dependencies

You need to install following dependencies on your system:

- Python 3.10
- Poetry

```bash
# Ubuntu 22.04 or newer, Debian bookworm
sudo apt install python3 python3-poetry

# Fedora (Fedora 36 ships python 3.10, Fedora 37 ships python 3.11)
sudo dnf install python3 python3-poetry

# Arch
sudo pacman -S python python-poetry

# Debian bullseye (Python 3.9)
sudo apt install python3 python3-pip
pip install --user poetry
# You may also need to add ~/.local/bin to your PATH

# Nix
nix develop
```

You can also install python from source, if you are adventurous enough.

### Virtual environment

Poetry manages virtual environments for you.

```bash
# Create venv and install dependencies
poetry install

# Enter shell with venv activated
poetry shell
```

### VSCode

Install VSCode or VSCodium.

Setup:

- Install `Python` extension
- Setup interpreter path
  - `CTRL + SHIFT + P`
  - Python: Select Interpreter
  - Click on poetry venv (should be marked with a star)
- Setup linter:
  - `CTRL + SHIFT + P`
  - Python: Select Linter
  - Pylama
- Setup autoformatter:
  - `CTRL + SHIFT + I`
  - Select `Use black` in the popup (bottom right)
- Setup pytest
  - `CTRL + SHIFT + P`
  - Python: configure tests
  - pytest
  - root directory: .

Alternatively create `.vscode/settings.json` file manually.

```json
{
  "python.linting.pylamaEnabled": true,
  "python.linting.enabled": true,
  "python.testing.pytestArgs": ["."],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "black"
}
```

### Test

This project comes with an extensive testsuite.

```bash
# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_post
```

### Run

`pyproject.toml` defines this application as installable.
It should be available in your PATH (inside poetry shell).

```bash
# Run the application
weight-tracker
```

## TODO

### Basic server

There are some static files, that should be served to the user.
Files are located at `weight_tracker/static`.
In the main function, you have a `static_dir` variable,
which already points at this location.
We can use the [builtin HTTP server](https://docs.python.org/3/library/http.server.html#http.server.HTTPServer)
and a [simple request handler](https://docs.python.org/3/library/http.server.html#http.server.SimpleHTTPRequestHandler)
to achieve this with minimal code.

```python
class Handler(SimpleHTTPRequestHandler):
    ...

httpd = HTTPServer(("localhost", 8080), Handler)
httpd.serve_forever()
```

You need to figure out, how to make the Handler serve the bundled static files.

### Schema validation

`weight-tracker/schema` defines 2 classes: `Record` and `Records`.
These are dataclasses, which represent `json` payload
sent between server and client.
They are also passed directly to the database classes.

```python
@dataclass
class Record:
    date: datetime.date
    value: float | int

@dataclass
class Records:
    records: list[Record]
```

We need to make sure, that fields are of correct type.
We can do it in the `__post_init__` method of the `Record` class.
We should also convert fields to proper types, if they are strings.

```python
def __post_init__(self):
    if isinstance(self.some_field, str):
        self.some_field = int(some_field)
    elif not isinstance(self.some_field, int):
        raise TypeError(f"some_field should be int, got {type(self.some_field)}")
```

```bash
# Run tests
pytest tests/test_schema.py
```

### In-memory database

We need a mechanism to store records. We can use a volitale storage for now.
The easiest way to implement this is using a dictionary.
By using `Record.date` as a key and `Record.value` as value,
we can easily access and enter new records.

```bash
# Run tests
pytest tests/test_database.py
```

### Inject database to the handler class

Use the same mechanism as for static_dir,
to inject database to the handler class.

### REST API

We need to imlpement 3 API endpoints.
You should use `do_GET` and `do_POST` methods in the `Handler`
for the implementation.

```python
import json
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Get request path
        self.path

        # Get query parameters
        url = urlparse(self.path)
        parse_qs(url.query)

        # Read json request body
        length = int(self.headers["Content-Length"])
        json.loads(self.rfile.read(length))

        # Set response status code
        self.send_response(HTTPStatus.OK)
        self.end_headers()

        # Write json response
        data = {"some": "data"}
        encoded_data = json.dumps(data).encode("utf-8")
        self.wfile.write(encoded_data)
```

#### POST /record

Put a single record into the database.

```text
Payload
{
    "date": "2023-01-23",
    "value": 88.1
}
```

#### GET /record

Get a single record (by date) from the database.
Date should be an URL query parameter.

```text
http://localhost:8080/record?date=2023-01-23
```

```text
Response
{
    "date": "2023-01-23",
    "value": 88.1
}
```

#### GET /records

Get all records from the database.

```text
http://localhost:8080/records
```

```text
Response
{
  "records": [
    {
      "date": "2023-01-23",
      "value": 88.1
    },
    {
      "date": "2023-01-24",
      "value": 88.3
    },
    {
      "date": "2023-01-25",
      "value": 88.5
    }
  ]
}
```

### Commandline args

In order to configure the application,
we can use commandline arguments.
Use [argparse](https://docs.python.org/3/library/argparse.html)
to handle the arguments.

Required arguments:

- --host hostname or IP address to listen on
- --port TCP port to listen on (should be a non-negative integer)
- --log-level level of the builtin logging module (use choices, one of INFO, WARN etc)
- --db-file path to a database file (must be a valid path)

```python
import argparse

@dataclass(init=False)
class Args:
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"
    db_file: Path = Path("db.sqlite3")

    def __init__(self, args: Sequence[str] | None = None):
        parser = argparse.ArgumentParser()
        parser.add_argument(...)
        parser.add_argument(...)
        parser.add_argument(...)
        parser.add_argument(...)
        parser.parse_args(args, namespace=self)
```

```bash
# Run tests
pytest tests/test_args.py
```

### Persistent database

Implement persistent database using SQLite3 module.
Alternatively just save `json` file instead.
