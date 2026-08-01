from unittest.mock import MagicMock, patch
import pytest

from stashies.weather_client import WeatherClient

def test_weather_client_fetch_historical():
    client = WeatherClient()
    mock_response_data = {
        "latitude": 40.71,
        "longitude": -74.00,
        "daily": {
            "time": ["2026-01-01", "2026-01-02"],
            "temperature_2m_max": [45.0, 48.2],
            "temperature_2m_min": [32.0, 35.6],
            "temperature_2m_mean": [38.5, 41.9]
        }
    }
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_response_data
        mock_get.return_value = mock_resp

        df_result = client.fetch_historical_temperatures(
            lat=40.71, lon=-74.00, start_date="2026-01-01", end_date="2026-01-02", units="F"
        )
        assert len(df_result) == 2
        assert "date" in df_result[0]
        assert "temp_mean" in df_result[0]
        assert "temp_max" in df_result[0]
        assert "temp_min" in df_result[0]
