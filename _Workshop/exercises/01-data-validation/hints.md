# Hints for Exercise 1: Data Validation

## Stuck? Here are some progressive hints:

### Hint 1: Where to Add Validation

The validation should happen in the `Message.__init__()` method, **after** stripping whitespace but **before** setting the attributes.

```python
def __init__(self, message_data):
    # Strip whitespace first
    user_id = message_data.user_id.strip()
    
    # Then validate
    if not user_id:
        raise ValueError("user_id cannot be empty")
    
    # Then assign
    self.user_id = user_id
```

### Hint 2: Validation Pattern

Use this pattern for each field:

```python
# 1. Extract and clean
field_value = message_data.field_name.strip()

# 2. Validate
if not field_value:
    raise ValueError("descriptive error message")

# 3. Assign
self.field_name = field_value
```

### Hint 3: Embedding Validation

For embeddings, validate **after** calling `generate_embedding()`:

```python
self.embeddings = generate_embedding(self.text)

# Validate dimensions
if not self.embeddings or len(self.embeddings) != 1536:
    actual_len = len(self.embeddings) if self.embeddings else 0
    raise ValueError(f"Invalid embedding dimensions. Expected 1536, got {actual_len}")
```

### Hint 4: Complete Solution Structure

```python
def __init__(self, message_data):
    # Validate user_id
    user_id = message_data.user_id.strip()
    if not user_id:
        raise ValueError("user_id cannot be empty")
    self.user_id = user_id
    
    # Validate conversation_id
    conversation_id = message_data.conversation_id.strip()
    if not conversation_id:
        raise ValueError("conversation_id cannot be empty")
    self.conversation_id = conversation_id
    
    # Validate text
    text = message_data.text.strip()
    if not text:
        raise ValueError("Message text cannot be empty")
    self.text = text
    
    # Other fields...
    self.type = message_data.type
    self.timestamp = self.parse_timestamp(message_data.timestamp)
    
    # Generate and validate embeddings
    self.embeddings = generate_embedding(self.text)
    if not self.embeddings or len(self.embeddings) != 1536:
        actual_len = len(self.embeddings) if self.embeddings else 0
        raise ValueError(f"Invalid embedding dimensions. Expected 1536, got {actual_len}")
```

### Hint 5: Testing Your Changes

Run the tests frequently to see which ones pass:

```bash
python -m pytest test_validation.py -v
```

Look for specific test failures - they tell you exactly what to fix!

### Hint 6: Common Mistakes

**Mistake 1:** Validating before stripping
```python
# Wrong - validates before cleaning
if not message_data.user_id:  # "   " is truthy!
    raise ValueError(...)
```

**Mistake 2:** Wrong error message
```python
# Wrong - doesn't match expected message
raise ValueError("user_id is invalid")  # Test expects "user_id cannot be empty"
```

**Mistake 3:** Not handling None embeddings
```python
# Wrong - crashes if embeddings is None
if len(self.embeddings) != 1536:  # TypeError if embeddings is None
```

### Still Stuck?

Compare your solution with `_Workshop/solutions/database/models.py` to see the full implementation with best practices.

## Key Concepts

**1. Fail Fast:** Validate as early as possible in the data flow

**2. Clear Errors:** Error messages should tell you exactly what's wrong

**3. Defense in Depth:** Don't trust that data is valid just because it was accepted by the API

**4. Schema-less ≠ Validation-less:** MongoDB won't enforce schema, but your app should!
