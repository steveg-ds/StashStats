# Stash Deletion Option Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement "Delete from Stash" button and confirmation flow in the Edit Stash Entry modal, calling Ravelry API deletion and purges on SQLite, Redis, and UI refresh.

**Architecture:** Add a red delete button to the edit modal footer, a confirmation browser dialog (`dcc.ConfirmDialog`), controller and model backend integration, and Dash callbacks to handle confirmation trigger and execution.

**Tech Stack:** Dash, Dash Bootstrap Components (DBC), Python, pytest

## Global Constraints

- Drop articles (a/an/the), filler (just/really/basically), pleasantries, hedging in communication.
- No placeholders, TBD, or TODOs.
- Keep tests aligned and fully passing at every step.

---

### Task 1: Update UI Layout and Components

Add `dcc.ConfirmDialog` and `dbc.Button` for delete option in edit modal.

**Files:**
- Modify: `stashies/components/edit_modal.py:209-224`

**Interfaces:**
- Consumes: None
- Produces: `edit-stash-delete-confirm` (dcc.ConfirmDialog) and `edit-stash-delete-btn` (dbc.Button) in edit modal layout.

- [ ] **Step 1: Write the test check**

We will mock rendering the layout and asserting the new components exist.
Add this test to `tests/test_stash_grouping.py`:

```python
def test_delete_components_in_modal_layout():
    from stashies.components.edit_modal import EditModal
    modal = EditModal(container_id="modal-test")
    layout = modal.create_init_layout()
    
    # Traverse layout children to find the delete components
    body_children = layout.children[1].children
    confirm_dialog = next((c for c in body_children if getattr(c, 'id', None) == "edit-stash-delete-confirm"), None)
    assert confirm_dialog is not None, "edit-stash-delete-confirm not found in ModalBody"
    assert confirm_dialog.message == "Are you sure you want to permanently delete this stash entry?"

    footer_children = layout.children[2].children
    delete_btn = next((c for c in footer_children if getattr(c, 'id', None) == "edit-stash-delete-btn"), None)
    assert delete_btn is not None, "edit-stash-delete-btn not found in ModalFooter"
    assert delete_btn.color == "danger"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_stash_grouping.py::test_delete_components_in_modal_layout -v`
Expected: FAIL with "AssertionError: edit-stash-delete-confirm not found in ModalBody" (or similar)

- [ ] **Step 3: Modify `stashies/components/edit_modal.py` to add elements**

Modify lines around 206-224 in `stashies/components/edit_modal.py`:

```python
                        html.Div(id="edit-stash-status-msg", className="text-info small mt-3"),
                        dcc.ConfirmDialog(
                            id="edit-stash-delete-confirm",
                            message="Are you sure you want to permanently delete this stash entry?"
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button("Delete Entry", id="edit-stash-delete-btn", color="danger", className="me-auto w-100 w-sm-auto mb-2 mb-sm-0"),
                        dbc.Button("Save Changes", id="edit-stash-save-btn", color="success", className="me-2 w-100 w-sm-auto mb-2 mb-sm-0"),
                        dbc.Button("Cancel", id="edit-stash-cancel-btn", color="secondary", outline=True, className="w-100 w-sm-auto"),
                    ],
                    className="flex-column flex-sm-row",
                ),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_stash_grouping.py::test_delete_components_in_modal_layout -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stashies/components/edit_modal.py tests/test_stash_grouping.py
git commit -m "feat: add delete button and confirm dialog to edit modal"
```

---

### Task 2: Implement Controller and DB/Model Connection Logic

Update `toggle_edit_modal` to include item `type` in the stored ID dictionary, and implement `handle_delete_stash`.

**Files:**
- Modify: `stashies/app_controller.py:751-769`
- Modify: `stashies/app_controller.py:643-644` (or append method)
- Modify: `tests/test_stash_grouping.py:90-114` (align expected assertions)

**Interfaces:**
- Consumes: `MODEL.delete_stash(stash_id, stash_type)`
- Produces: `AppController.handle_delete_stash(self, stash_id, stash_type) -> Tuple[str, bool]`
- Produces: `AppController.toggle_edit_modal` returning ID dictionary with type key.

- [ ] **Step 1: Write test for `handle_delete_stash` and verify `toggle_edit_modal` type updates**

Update `tests/test_stash_grouping.py`:
- In `test_toggle_edit_modal_robust_matching` modify Assertions:
```python
    # Test case 2: Valid edit button click and match found (with numeric/string matching)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": 123, "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1, "type": "yarn"}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": 123, "name": "Soft Wool", "type": "yarn"}
```
- In `test_toggle_edit_modal_robust_matching` update Test case 3 as well:
```python
    # Test case 3: Match with mismatched types (index string vs integer ID)
    res = controller.toggle_edit_modal(
        edit_clicks=[1],
        cancel_click=None,
        store_data_list=[
            {"id": "123", "skeins": 5.0, "name": "Soft Wool", "colorway": "Red", "dye_lot": "A", "location": "Box", "notes": "notes", "status_id": 1, "type": "yarn"}
        ],
        btn_ids=[{"index": 123}],
        triggered_id='{"index": 123, "type": "edit-btn"}.n_clicks'
    )
    assert res[0] is True
    assert res[1] == {"id": "123", "name": "Soft Wool", "type": "yarn"}
```
- Add a unit test for `handle_delete_stash` at the bottom of `tests/test_stash_grouping.py`:
```python
def test_handle_delete_stash():
    controller = AppController(header_id="h", search_id="s", result_id="r")
    controller.MODEL = MagicMock()
    
    # Mock model's delete_stash return value
    controller.MODEL.delete_stash.return_value = True
    msg, is_open = controller.handle_delete_stash(123, "yarn")
    assert msg == "Entry deleted successfully."
    assert is_open is False
    controller.MODEL.delete_stash.assert_called_once_with(123, "yarn")

    # Mock delete failure
    controller.MODEL.delete_stash.reset_mock()
    controller.MODEL.delete_stash.return_value = False
    msg, is_open = controller.handle_delete_stash(123, "yarn")
    assert msg == "Failed to delete entry."
    assert is_open is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_stash_grouping.py -v`
Expected: FAIL due to assertions missing `"type"` key or `handle_delete_stash` missing attribute on controller.

- [ ] **Step 3: Modify `stashies/app_controller.py`**

In `stashies/app_controller.py`:
Modify line 753 (within `toggle_edit_modal`):
```python
            {"id": sd.get("id"), "name": yarn_name, "type": sd.get("type")},
```
And implement `handle_delete_stash` method (add below `handle_save_edit` or somewhere suitable):
```python
    def handle_delete_stash(self, stash_id: Union[str, int], stash_type: str = "yarn") -> Tuple[str, bool]:
        """
        Delete a stash entry and return status and modal visibility.
        """
        try:
            success = self.MODEL.delete_stash(stash_id, stash_type)
            if success:
                self.LOGGER.info(f"[WRITE] stash_id={stash_id} type={stash_type} | deleted successfully")
                return "Entry deleted successfully.", False
            else:
                self.LOGGER.warning(f"[WRITE FAILED] stash_id={stash_id} type={stash_type} | delete failed")
                return "Failed to delete entry.", True
        except Exception as e:
            self.LOGGER.error(f"[WRITE ERROR] stash_id={stash_id} type={stash_type} | {e}")
            return f"Error: {e}", True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_stash_grouping.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stashies/app_controller.py tests/test_stash_grouping.py
git commit -m "feat: implement controller delete handling and update edit store data format"
```

---

### Task 3: Wire Dash Callbacks in app.py and Verify End-to-End

Wire callbacks in `app.py` to trigger confirmation dialog and execute deletion.

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `AppController.handle_delete_stash`
- Produces: Callbacks for `edit-stash-delete-btn` and `edit-stash-delete-confirm`.

- [ ] **Step 1: Write integration tests for delete flow**

Modify `tests/test_e2e.py` to verify deletion. Let's add a test:

```python
def test_delete_stash_flow():
    from app import save_stash_edit
    # We can mock CONTROLLER's handle_delete_stash method in this test
    # to simulate the execution of delete callback.
    import stashies.app_controller
    from unittest.mock import patch
    
    with patch("app.CONTROLLER.handle_delete_stash") as mock_delete:
        mock_delete.return_value = ("Entry deleted successfully.", False)
        
        # We need to import the newly defined delete callback from app
        # Let's inspect app callbacks. We'll declare the handler function below.
        from app import handle_delete_confirm_submit
        
        res_msg, is_open, new_trigger = handle_delete_confirm_submit(
            submit_n_clicks=1,
            stash_id={"id": 123, "name": "Yarn A", "type": "yarn"},
            trigger_data=0
        )
        assert res_msg == "Entry deleted successfully."
        assert is_open is False
        assert new_trigger == 1
        mock_delete.assert_called_once_with(123, "yarn")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. .venv/bin/pytest tests/test_e2e.py::test_delete_stash_flow -v`
Expected: FAIL with "ImportError: cannot import name 'handle_delete_confirm_submit' from 'app'"

- [ ] **Step 3: Modify `app.py` to add callbacks**

Add the callbacks in `app.py` before the `if __name__ == "__main__":` block:

```python
@callback(
    Output("edit-stash-delete-confirm", "displayed"),
    Input("edit-stash-delete-btn", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_delete_confirm(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    return True


@callback(
    Output("edit-stash-status-msg", "children", allow_duplicate=True),
    Output("edit-stash-modal", "is_open", allow_duplicate=True),
    Output("stash-update-trigger", "data", allow_duplicate=True),
    Input("edit-stash-delete-confirm", "submit_n_clicks"),
    State("edit-stash-id-store", "data"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def handle_delete_confirm_submit(submit_n_clicks, stash_id, trigger_data):
    if not submit_n_clicks or not stash_id:
        raise PreventUpdate
    
    actual_id = stash_id.get("id") if isinstance(stash_id, dict) else stash_id
    stash_type = stash_id.get("type", "yarn") if isinstance(stash_id, dict) else "yarn"
    
    res_msg, is_open = CONTROLLER.handle_delete_stash(actual_id, stash_type)
    
    new_trigger_data = trigger_data
    if not is_open:
        new_trigger_data = (trigger_data or 0) + 1
        
    return res_msg, is_open, new_trigger_data
```

- [ ] **Step 4: Run all tests to verify everything passes**

Run: `PYTHONPATH=. .venv/bin/pytest tests/ -v`
Expected: 16 passed.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_e2e.py
git commit -m "feat: wire delete button confirmation and submit callbacks"
```
