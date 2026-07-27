## Yarn Weights

### Implementation
- `stashies/client/yarn_weights.py` implements `get_yarn_weights()`
- Returns structured list of yarn weight categories
- Supports type hints for Python 3.10+

### Ravelry API Endpoints
- GET `/yarn_weights.json` - List all yarn weights

### Client Usage
```python
from stashies.client import RavelryClient

client = RavelryClient(api_username="user", api_key="key")
weights = client.get_yarn_weights()
```