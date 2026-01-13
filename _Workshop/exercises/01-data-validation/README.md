# Exercise 1: Data Validation & Error Handling

**Time Estimate:** 20-30 minutes  
**Difficulty:** ⭐⭐ Beginner-Intermediate

## Learning Objectives

By completing this exercise, you will:
- Understand why data validation is critical in schema-less databases like MongoDB
- Learn to implement defensive programming patterns in Python
- Practice error handling with descriptive error messages
- Ensure data consistency before database operations

## Problem Statement

The current implementation of the `Message` class in `database/models.py` accepts invalid data without validation. This can lead to:

1. **Empty user IDs** being stored in MongoDB
2. **Empty message text** being stored
3. **Malformed embeddings** (wrong dimensions or empty arrays)
4. **Silent failures** that are hard to debug

### Current Issues

```python
# These should FAIL but currently SUCCEED:

# Issue 1: Empty user_id
message = Message(MessageInput(
    user_id="",  # Empty!
    conversation_id="test",
    type="human",
    text="Hello",
    timestamp=None
))

# Issue 2: Empty text
message = Message(MessageInput(
    user_id="alice",
    conversation_id="test",
    type="human",
    text="",  # Empty!
    timestamp=None
))

# Issue 3: Wrong embedding dimensions
# (This happens if generate_embedding() returns wrong size)
# Should be 1536 dimensions, but could be 0 or wrong size
```

## Your Task

Enhance the `Message` class to validate all inputs before storing to MongoDB.

### Requirements

1. **Validate `user_id`**
   - Must not be empty after stripping whitespace
   - Raise `ValueError` with message: "user_id cannot be empty"

2. **Validate `conversation_id`**
   - Must not be empty after stripping whitespace
   - Raise `ValueError` with message: "conversation_id cannot be empty"

3. **Validate `text`**
   - Must not be empty after stripping whitespace
   - Raise `ValueError` with message: "Message text cannot be empty"

4. **Validate `embeddings`**
   - Must be a non-empty list
   - Must contain exactly 1536 elements (Titan Embeddings v1 dimension)
   - Raise `ValueError` with message: "Invalid embedding dimensions. Expected 1536, got {actual}"

## File to Modify

`database/models.py` - Update the `Message.__init__()` method

## Running Tests

```bash
cd /Users/peter.do/ai-memory/_Workshop/exercises/01-data-validation
python -m pytest test_validation.py -v
```

All tests should pass after your implementation.

## Success Criteria

✅ All 6 test cases pass  
✅ Code raises descriptive `ValueError` for each invalid input  
✅ Valid inputs still work correctly  
✅ Error messages are clear and helpful

## MongoDB Context

**Why This Matters:**

MongoDB is schema-less, meaning it won't enforce data types or required fields. Unlike SQL databases with NOT NULL constraints, MongoDB will happily store:
- Empty strings
- Null values
- Mismatched types

This makes **application-level validation critical** for:
- Data consistency
- Query performance (empty strings still get indexed)
- Debugging (clear errors vs. silent failures)
- Vector search (wrong dimensions = crash)

## Hints

Need help? Check `hints.md` in this directory.

## Next Steps

After completing this exercise:
1. Run the tests to verify your solution
2. Compare with the solution in `_Workshop/solutions/database/models.py`
3. Read the implementation notes to understand design decisions
4. Move on to Exercise 2: Index Health Monitoring

---

**Pro Tip:** In production, you'd also add:
- Type hints for better IDE support
- Logging for validation failures
- Metrics tracking (how often validation fails)
- Custom exception classes for different error types
