---
name: documentation-templates
description: "Documentation templates and structure guidelines. README, API docs, code comments, and AI-friendly documentation."
risk: safe
source: community
date_added: "2026-02-27"
origin: https://github.com/sickn33/antigravity-awesome-skills
---

# Documentation Templates

> Templates and structure guidelines for common documentation types.

---

## 1. README Structure

### Essential Sections (Priority Order)

| Section | Purpose |
|---------|---------|
| **Title + One-liner** | What is this? |
| **Quick Start** | Running in <5 min |
| **Features** | What can I do? |
| **Configuration** | How to customize |
| **API Reference** | Link to detailed docs |
| **Contributing** | How to help |
| **License** | Legal |

---

## 2. Python Docstring Template (Google style)

```python
def function_name(param1: type, param2: type) -> return_type:
    """Brief one-line summary.

    Longer description if needed. Explain non-obvious behavior,
    side effects, or important context.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is invalid.
        KeyError: When key not found.

    Example:
        >>> result = function_name("foo", 42)
        >>> print(result)
        'foo-42'
    """
```

## 3. Module-level docstring template

```python
"""Module short description.

Longer description of what this module contains, its role in the
architecture, and key classes/functions exported.

Typical usage:
    from stashies.model import Model
    model = Model(base_url, auth)
    stash = model.get_stash_list(username)
"""
```

## 4. Class docstring template

```python
class ClassName:
    """Brief class description.

    Longer description of class purpose, role in MVC, and
    key behaviors.

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.
    """
```

## 5. When to comment inline

| ✅ Comment | ❌ Don't Comment |
|-----------|-----------------|
| Non-obvious algorithm steps | `x = 1  # set x to 1` |
| Business logic rationale | Simple assignments |
| Workarounds with ticket refs | Self-explanatory code |
| API quirks or gotchas | Type-annotated signatures |
