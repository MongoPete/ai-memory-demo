# Exercise 5: Embedding Dimension Validation

**Time:** 30-40 min | **Difficulty:** ⭐⭐

## Problem
Wrong dimension embeddings crash vector search. Need validation.

## Task
Add embedding validation in `database/models.py` and `services/bedrock_service.py`

### Requirements
- Validate embeddings are list of floats
- Validate exactly 1536 dimensions (Titan v1)
- Handle empty embeddings gracefully
- Clear error messages

### Tests
```bash
pytest exercises/05-embedding-validation/test_embeddings.py -v
```

## MongoDB Context
- Vector search requires exact dimensions matching index config
- Dimension mismatch = silent failures or crashes
- Always validate before storing

See hints.md!
