# Exercise 6: Async Memory Pruning

**Time:** 40-50 min | **Difficulty:** ⭐⭐⭐⭐

## Problem
Memory pruning blocks API responses. Need async background tasks.

## Task
Convert `prune_memories()` to background task

### Requirements
- Create `services/background_tasks.py` for task management
- Make pruning non-blocking using `asyncio` or `threading`
- Add logging for pruning operations
- API returns immediately while pruning runs in background

### Tests
```bash
pytest exercises/06-async-pruning/test_async_ops.py -v
```

## MongoDB Context
- MongoDB operations are async-safe
- Use asyncio for I/O-bound tasks
- Background tasks improve UX

See hints.md!
