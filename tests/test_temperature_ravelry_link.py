from unittest.mock import MagicMock, patch
import pytest

from stashies.model import Model

def test_create_temperature_ravelry_project():
    model = Model()
    with patch.object(model, "create_ravelry_project") as mock_create:
        mock_create.return_value = {"project": {"id": 12345, "name": "NYC Temp Blanket"}}
        res = model.create_temperature_ravelry_project(
            name="NYC Temp Blanket",
            notes="Temperature Blanket 2026",
            stash_ids=["101", "102"]
        )
        assert res is not None
        assert res.get("project", {}).get("id") == 12345
        # Verify create_ravelry_project was actually called with the correct project name
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        # The name should be passed through
        assert call_args is not None, "create_ravelry_project must have been called"
        # Check name was included in the call
        all_args = list(call_args.args) + list(call_args.kwargs.values())
        assert any("NYC Temp Blanket" in str(a) for a in all_args), \
            "create_ravelry_project should be called with the project name"
