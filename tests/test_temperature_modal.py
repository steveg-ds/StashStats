import pytest
from stashies.components.temperature_modal import TemperatureModal, calculate_tier_yardage

def test_calculate_tier_yardage():
    # 50 days in tier, 10 yards/row, 1 row/day, 10% buffer
    total_yards, skeins_needed = calculate_tier_yardage(
        day_count=50, yards_per_row=10.0, rows_per_day=1, buffer_pct=0.10, yards_per_skein=200.0
    )
    assert total_yards == 550.0  # 500 * 1.10
    assert skeins_needed == 3    # ceil(550 / 200) = 3

def test_temperature_modal_instantiation():
    modal = TemperatureModal(container_id="test-temp-modal")
    layout = modal.create_modal_layout()
    assert layout is not None
