# Exercise 3: Pagination for Scale

**Time:** 40-50 min | **Difficulty:** ⭐⭐⭐

## Problem
Loading all messages crashes with large conversations. No pagination = poor performance.

## Task
Add pagination to `get_conversation_history()` in `services/conversation_service.py`

### Requirements
- Accept `page` and `page_size` parameters
- Use `.skip()` and `.limit()` for cursor-based pagination  
- Return pagination metadata: `{messages: [], pagination: {page, page_size, total, has_next}}`

### Tests
```bash
pytest exercises/03-pagination/test_pagination.py -v
```

## MongoDB Context
- `.skip()` + `.limit()` = basic pagination
- Alternative: cursor-based with `_id` > last_id (faster for large datasets)
- Always include total count for UI

See hints.md for help!
