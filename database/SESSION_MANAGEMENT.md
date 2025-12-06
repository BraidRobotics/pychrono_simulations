# Database Session Management

This project uses SQLAlchemy for database access with multiple session management patterns optimized for different use cases.

## Session Patterns

### 1. Scoped Session (Recommended for Scripts)

Use the `scoped_session()` context manager for short-lived scripts that need automatic cleanup:

```python
from database.session import scoped_session

with scoped_session() as session:
    # Query and modify data
    series = session.query(ExperimentSeries).all()
    # Changes are automatically committed when exiting
    # Session is automatically closed on exit
```

**Benefits:**
- Automatic commit on success
- Automatic rollback on exceptions
- Automatic cleanup (close)
- Clean, readable code

**Use for:**
- Meta scripts (graph generation, data creation)
- Simple database operations
- When you need guaranteed cleanup

### 2. Global Singleton Session

Use `get_session()` and `close_global_session()` for long-running processes:

```python
from database.session import get_session, close_global_session

session = get_session()  # Gets or creates singleton
try:
    # Use session for multiple operations
    experiment_series = session.query(ExperimentSeries).first()
    # ... do work ...
    session.commit()
finally:
    close_global_session()  # Clean up at end
```

**Benefits:**
- Single session reused across function calls
- Lower overhead for many operations
- Works across multiprocessing boundaries

**Use for:**
- Long-running experiment loops
- Multiprocessing workers
- When session needs to persist across multiple function calls

### 3. Flask Integration

Flask uses request-scoped sessions automatically:

```python
@app.before_request
def create_session():
    g.db = SessionLocal()

@app.teardown_appcontext
def teardown_session(exception=None):
    if hasattr(g, 'db'):
        g.db.close()
```

## Migration Guide

### Old Pattern (Manual Management)
```python
session = SessionLocal()
try:
    # do work
    session.commit()
finally:
    session.close()
```

### New Pattern (Scoped)
```python
with scoped_session() as session:
    # do work
    # auto-commits and closes
```

### New Pattern (Singleton)
```python
session = get_session()
# do work
session.commit()
close_global_session()  # Call once at program end
```

## Examples from Codebase

### Graph Generation
```python
# meta/generate_aggregate_graphs.py
with scoped_session() as session:
    generate_all_graphs(session)
```

### Experiment Execution
```python
# experiments/run_experiments.py
def run_a_single_experiment(name, config):
    session = get_session()
    experiment_loop(session, config)
    close_global_session()
```

### Data Creation
```python
# meta/create_experiment_series.py
with scoped_session() as session:
    for item in items:
        insert_data(session, item)
    # Auto-commits all inserts
```

## Important Notes

1. **Never mix patterns** - Choose one pattern per script/module
2. **Commit explicitly** when using singleton pattern
3. **Scoped sessions auto-commit** - no need to call `session.commit()`
4. **Global session is per-process** - each multiprocessing worker gets its own
5. **Flask sessions are per-request** - don't use global session in Flask routes

## Common Mistakes

### ❌ Don't: Forget to close global session
```python
session = get_session()
# ... work ...
# Missing: close_global_session()
```

### ✅ Do: Always close in finally block
```python
session = get_session()
try:
    # ... work ...
finally:
    close_global_session()
```

### ❌ Don't: Call commit in scoped session
```python
with scoped_session() as session:
    # ... work ...
    session.commit()  # Unnecessary, auto-commits
```

### ✅ Do: Let scoped session handle it
```python
with scoped_session() as session:
    # ... work ...
    # Auto-commits on successful exit
```
