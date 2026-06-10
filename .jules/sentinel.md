## 2025-05-22 - [Secure Error Handling]
**Vulnerability:** Raw exception strings leaked to UI in `AppController`.
**Learning:** `handle_add_to_stash` and `handle_save_edit` returned `str(e)`, exposing internal logic/paths to frontend.
**Prevention:** Always catch exceptions, log details server-side, return generic user-facing messages.
