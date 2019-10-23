import requests
import time


class TimeZoneAPI:
    """Google timezone api

    For more information:
    https://developers.google.com/maps/documentation/timezone/intro

    Args:
        api_key (str): Google api key
    """
    _BASE_URL = 'https://maps.googleapis.com/maps/api/timezone/json'

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("TimeZoneAPI required api_key argument")
        self._api_key = api_key

    def get_timezone(self, latitude, longitude):
        """Get timezone info by latitude and longitude

        Args:
            latitude (int | float): Latitude
            longitude (int | float): longitude

        Returns:
            Dict: Timezone data
        """
        params = {
            'location': f'{latitude},{longitude}',
            'timestamp': time.time(),
            'key': self._api_key,
        }

        response = requests.get(self._BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            data = {
                "status": response.status_code,
                "errorMessage": response.reason,
            }

        return data


