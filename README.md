# fastapi-react-udemy
## Build virtual environment
### Make virtual environment
```bash
python -m venv venv
```

### Activate
```bash
source venv/bin/activate
```
or
```bash
source venv/bin/activate.fish
```

### Deactivate
```bash
deactivate
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run server
```bash
uvicorn main:app --reload
```