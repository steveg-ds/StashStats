"""Open-Meteo Historical Weather API client for Temperature Blanket tracking."""
from typing import Any, Dict, List, Optional
import requests
from .base import Base


class WeatherClient(Base):
    """
    Client for querying historical weather data from Open-Meteo Archive API.
    Does not require an API key.
    """

    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

    def fetch_historical_temperatures(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        units: str = "F"
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily high, low, and mean temperatures for a given latitude, longitude, and date range.

        Args:
            lat (float): Latitude coordinate.
            lon (float): Longitude coordinate.
            start_date (str): Start date string YYYY-MM-DD.
            end_date (str): End date string YYYY-MM-DD.
            units (str): Temperature unit - 'F' for Fahrenheit, 'C' for Celsius.

        Returns:
            List[Dict[str, Any]]: List of daily records containing date, temp_max, temp_min, and temp_mean.
        """
        self.LOGGER.debug(
            f"Fetching historical weather: lat={lat}, lon={lon}, start={start_date}, end={end_date}, units={units}"
        )
        temp_unit = "fahrenheit" if units.upper() == "F" else "celsius"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"],
            "temperature_unit": temp_unit,
            "timezone": "auto"
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            daily_data = data.get("daily", {})

            times = daily_data.get("time", [])
            max_temps = daily_data.get("temperature_2m_max", [])
            min_temps = daily_data.get("temperature_2m_min", [])
            mean_temps = daily_data.get("temperature_2m_mean", [])

            results = []
            for i in range(len(times)):
                results.append({
                    "date": times[i],
                    "temp_max": max_temps[i] if i < len(max_temps) else None,
                    "temp_min": min_temps[i] if i < len(min_temps) else None,
                    "temp_mean": mean_temps[i] if i < len(mean_temps) else None,
                })
            self.LOGGER.info(f"Successfully fetched {len(results)} daily weather records")
            return results

        except Exception as e:
            self.LOGGER.error(f"Failed to fetch historical weather data: {e}")
            return []
