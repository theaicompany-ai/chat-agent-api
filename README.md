## start command

```
python3 -m venv .venv

source .venv/bin/activate

pip3 install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
# Chat Agent Server

## Tech Stack:

- Language: `Python`
- HTTP Server: `FastAPI`
- Database: `MongoDB`