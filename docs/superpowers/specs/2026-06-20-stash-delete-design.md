# Stash Entry Deletion Design

Specification for implementing "Delete from Stash" functionality.

## Requirements

1. **Delete Button**: A "Delete Entry" button in the Edit Stash Entry modal footer.
2. **Confirmation**: A confirmation dialog prompting the user before actual deletion.
3. **Backend Deletion**:
   - Call Ravelry API (`DELETE`) for the stash yarn or fiber.
   - Delete records from SQLite `original_values` and `stash_history` tables.
   - Invalidate Redis caches (`stash_detail` and `stash_list`).
4. **UI Update**:
   - Close modal on successful deletion.
   - Refresh the personal stash list and analytics tab.

## Design

### 1. UI Components (`stashies/components/edit_modal.py`)
- Add `dcc.ConfirmDialog` under `ModalBody`:
  ```python
  dcc.ConfirmDialog(
      id="edit-stash-delete-confirm",
      message="Are you sure you want to permanently delete this stash entry?"
  )
  ```
- Add `dbc.Button` in `ModalFooter`:
  ```python
  dbc.Button(
      "Delete Entry",
      id="edit-stash-delete-btn",
      color="danger",
      className="me-auto w-100 w-sm-auto mb-2 mb-sm-0"
  )
  ```
  *(Note: using `me-auto` to push it to the left while keeping Save/Cancel on the right).*

### 2. Controller Logic (`stashies/app_controller.py`)
- Update `toggle_edit_modal` so `edit-stash-id-store` includes `"type"`:
  ```python
  {"id": sd.get("id"), "name": yarn_name, "type": sd.get("type")}
  ```
- Implement `handle_delete_stash(self, stash_id, stash_type) -> Tuple[str, bool]`:
  - Call `self.MODEL.delete_stash(stash_id, stash_type)`.
  - On success, return `("Entry deleted successfully.", False)`.
  - On failure, return `("Failed to delete entry.", True)`.

### 3. Application Callbacks (`app.py`)
- Callback for confirming deletion:
  - Input: `edit-stash-delete-btn.n_clicks`
  - Output: `edit-stash-delete-confirm.displayed`
- Callback for executing deletion:
  - Input: `edit-stash-delete-confirm.submit_n_clicks`
  - State: `edit-stash-id-store.data` (to fetch `id` and `type`)
  - State: `stash-update-trigger.data`
  - Output: `edit-stash-status-msg.children` (allow_duplicate=True)
  - Output: `edit-stash-modal.is_open` (allow_duplicate=True)
  - Output: `stash-update-trigger.data`

### 4. Tests (`tests/test_stash_grouping.py`)
- Align mock data assertions since `edit-stash-id-store` now has `"type"`.
