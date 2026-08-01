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
