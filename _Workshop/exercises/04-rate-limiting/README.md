# Exercise 4: Rate Limiting with MongoDB

**Time:** 45-60 min | **Difficulty:** ⭐⭐⭐⭐

## Problem
No protection against API abuse. Need rate limiting.

## Task
Create `services/rate_limiter.py` that uses MongoDB for rate limiting

### Requirements
- `check_rate_limit(user_id, action, limit, window_minutes)` returns (allowed, message)
- Store rate limit records in `rate_limits` collection
- Create TTL index on `expires_at` field
- Return 429 status when rate limited

### Tests
```bash
pytest exercises/04-rate-limiting/test_rate_limiting.py -v
```

## MongoDB Context
- TTL indexes auto-delete expired documents
- Perfect for rate limiting, sessions, temporary data
- `db.collection.createIndex({expires_at: 1}, {expireAfterSeconds: 0})`

See hints.md!
