import requests

from . import limits


class Reddit:
    """Class to work with reddit api

    For more information: https://www.reddit.com/dev/api/
    """
    _BASE_URL = "https://www.reddit.com/r/"
    _HEADERS = {"User-agent": "TopSubredditBot"}

    def __init__(self):
        pass

    def get_json(self, url, params):
        """Get

        Args:
            url (str): Url for request
            params (Dict): Get request params

        Returns:
            Dict: Response data
        """
        response = requests.get(url, headers=self._HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            data = {}
        return data

    @staticmethod
    def _check_argument(value, expected_value):
        """Check arguments for request

        Args:
            value (Tuple | List): Value to check
            expected_value (Tuple | list): Available data

        Raises:
            TypeError: if data is not valid
        """
        if isinstance(expected_value, (tuple, list)):
            if value not in expected_value:
                raise TypeError(
                    f"Expected one of {expected_value!r}, got {type(value).__name__}"
                )

    def is_subreddit_has_posts(self, subreddit):
        """Check if subreddit has posts

        Args:
            subreddit (str): Subreddit

        Returns:
            bool: True if subreddit has posts
        """
        url = f"{self._BASE_URL}{subreddit}/top.json"
        data = self.get_json(url, {"t": "day", "limit": 1})
        if data.get("data", {}).get("children"):
            return True
        return False

    def get_subreddit_top_posts(self, subreddit, sort="top", t="day", limit=5):
        """Get subreddit posts

        Args:
            subreddit (str): Subreddit
            sort (str): Sort key (one of "relevance", "hot", "top", "new", "comments")
            t (str): Search period (one of "hour", "day", "week", "month", "year", "all")
            limit (int): Posts limit (1 - 100)

        Returns:
            Dict: Response data
        """
        self._check_argument(sort, limits.sort)
        self._check_argument(t, limits.t)
        self._check_argument(limit, limits.limit)

        url = f"{self._BASE_URL}{subreddit}/top.json"
        params = {"sort": sort, "t": t, "limit": limit}

        return self.get_json(url, params)
