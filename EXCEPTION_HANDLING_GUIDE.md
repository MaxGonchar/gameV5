# Exception Handling Development Guide

**Project:** gameV5 Backend  
**Version:** 1.0  
**Date:** November 2025

## 🎯 Quick Reference for AI Coding Sessions

This guide ensures consistent exception handling across the gameV5 backend. **Always follow these patterns when writing or modifying code.**

---

## 📋 Custom Exception Hierarchy

Use **only** these custom exceptions from `app.exceptions`:

```python
from app.exceptions import (
    CoreException,           # Base class - rarely used directly
    DataValidationException, # Invalid input data (400)
    EntityNotFoundException, # Resource not found (404) 
    BusinessLogicException,  # Business rule violations (422)
    ExternalServiceException,# API/LLM failures (502/503)
    ServiceException,        # Internal service errors (500)
    InitializationException  # Setup/config failures (500)
)
```

---

## ✅ Exception Usage Patterns

### **DAO Layer** (Data Access)
```python
# File operations
raise FileOperationException("Cannot read character file", {"path": file_path})

# Data not found
raise EntityNotFoundException("Character not found", {"id": character_id})

# Invalid data structure
raise DataValidationException("Invalid YAML format", {"field": "name"})
```

### **Service Layer** (Business Logic)
```python
# Wrap DAO exceptions with business context
try:
    character = await character_dao.get(id)
except EntityNotFoundException as e:
    raise BusinessLogicException("Cannot start story without character")

# External service failures
raise ExternalServiceException("AI service unavailable", {"provider": "venice"})
```

### **API Layer** (HTTP Responses)
```python
# Map exceptions to HTTP status codes
except EntityNotFoundException:
    raise HTTPException(status_code=404, detail="Story not found")
except DataValidationException as e:
    raise HTTPException(status_code=400, detail=f"Invalid data: {e.message}")
```

---

## 🚫 **NEVER DO**

❌ `raise Exception("generic error")`  
❌ `raise ValueError("some error")`  
❌ `except Exception as e:` (too broad)  
❌ `print(f"Error: {e}")` (use logging)

---

## ✅ **ALWAYS DO**

✅ Use specific custom exceptions  
✅ Include error details dict  
✅ Use proper logging with `get_logger(__name__)`  
✅ Follow dependency-first approach (check what exceptions are actually raised)  

---

## 🔧 Exception Creation Pattern

```python
# Standard pattern with details
raise DataValidationException(
    "Character validation failed", 
    {"field": "name", "value": invalid_value, "constraint": "non-empty"}
)

# With error wrapping utility
from app.exceptions import wrap_exception
try:
    result = external_api_call()
except requests.RequestException as e:
    raise wrap_exception(e, ExternalServiceException, "API call failed")
```

---

## 📊 HTTP Status Code Mapping

| Exception Type | HTTP Status | Usage |
|---------------|-------------|-------|
| `EntityNotFoundException` | 404 | Resource not found |
| `DataValidationException` | 400 | Invalid request data |
| `BusinessLogicException` | 422 | Business rule violation |
| `ExternalServiceException` | 502/503 | External service issues |
| `ServiceException` | 500 | Internal service error |
| `InitializationException` | 500 | Setup/config failure |

---

## 🧪 Testing Exceptions

```python
import pytest
from app.exceptions import DataValidationException

def test_character_validation():
    with pytest.raises(DataValidationException) as exc_info:
        character_service.validate_character(invalid_data)
    
    assert "name" in exc_info.value.details
```

---

## ⚡ Quick Integration Checklist

When writing new code:

- [ ] Import specific exceptions from `app.exceptions`
- [ ] Use custom exceptions instead of built-in ones
- [ ] Include error details dict for debugging
- [ ] Add proper logging with context
- [ ] Map to appropriate HTTP status in API layer
- [ ] Test exception scenarios

---

**💡 Remember:** This system is complete and standardized. Do not create new exception types - use existing ones with appropriate details.