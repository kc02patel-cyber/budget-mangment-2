# Global Budgeting Backend

### Run locally
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

### Endpoints
- POST `/items/` → create income/expense item
- GET `/items/` → list all items
- GET `/items/{id}` → retrieve item by ID
- DELETE `/items/{id}` → delete item
