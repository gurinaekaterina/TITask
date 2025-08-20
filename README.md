## Getting Started

1. **Clone the repository**
```bash
git clone https://github.com/gurinaekaterina/TITask.git
cd TITask
```

2. **Create the .env file**

Before running the app, create a .env file in the project root based on .env.example.

## Running the project

**Option A. locally (without Docker)**

This project requires `uv`.
`uv` is a fast Python package manager. 
- If you prefer not to use uv, you can use plain pip in a virtual environment:

```
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -e .
alembic -c alembic/alembic.ini upgrade head
uvicorn app.main:app --reload
```
Application will be available at http://127.0.0.1:8000/frontend/

- If you want to use `uv` and it's not installed yet, please refer to [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

    After `uv` is installed follow these instructions:
```
uv pip install -e .

# run migrations
alembic -c alembic/alembic.ini upgrade head

# start the server
uvicorn app.main:app --reload
```

Application will also be available at http://127.0.0.1:8000/frontend/

**Option B. Run with Docker Compose**

```
docker compose up --build
```

The application will be available at:
http://localhost:8080/frontend

## Running tests

To run tests please use 
```
pytest
```

Or if you're using `uv` you may do
```
uv run pytest
```