## Ravelry API Client

### Installation
```bash
pip install stashies-client
```

### Authentication
- API key: `{{RAVEIR_KEY}}` in environment variables
- OAuth 2.0 token support

### Key Endpoints
1. GET /stashes - List all stashes
2. POST /stashes - Create new stash
3. GET /stashes/{id} - Detail specific stash
4. PUT /stashes/{id}/update - Update stash quantities
5. DELETE /stashes/{id} - Remove stash

### Error Handling
- 401: Invalid API key
- 422: Stash format invalid
- 503: Rate limit exceeded