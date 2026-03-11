# Digitalisierungsfabrik

Working prototype for the Digitalisierungsfabrik system described in `digitalisierungsfabrik_systemdefinition.md`, implemented against the baseline in `hla_architecture.md`.

## Repository layout

```text
backend/   FastAPI backend
frontend/  React + Vite frontend
agent-docs/  Agent task, decision, and planning documentation
```

## Local development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tests

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```
