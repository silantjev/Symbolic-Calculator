import logging
import requests

DEFAULT_URL = 'http://127.0.0.1:8000'

class CalcHttpRequester:
    def __init__(self, base_url=None, logger=None):
        if base_url is None:
            self.base_url = DEFAULT_URL
        else:
            self.base_url = base_url

        if logger is None:
            logger_name = self.__class__.__name__
            self.logger = make_logger(name=logger_name, file=False, console=False, level=logging.WARNING)
        else:
            self.logger = logger

        self.data = {}

    def get(self, endpoint, params=None):
        if params is None:
            params = {}
        try:
            response = requests.get(
                    f"{self.base_url}/calc/{endpoint}",
                    params=params,
                    timeout=5,
                )
        except requests.exceptions.ConnectionError as exc:
            self.logger.error("Connection to '%s' failed: %s", self.base_url, exc, exc_info=False)
            raise ConnectionError("Connection failed: run api_service")

        if response.status_code != 200:
            self.logger.error("Error while getting sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")

        return response.json()

    def put_state(self):
        response = requests.put(
                f"{self.base_url}/calc/put_state",
                json=self.data,
                timeout=5,
            )

        if response.status_code == 400 and "detail" in response.json() and "Error" in response.json()["detail"]:
            return response.json()["detail"]['Error']

        if response.status_code != 200:
            self.logger.error("Error while putting sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")


        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", self.data)
        return ""

    def post(self, endpoint, json):
        response = requests.post(
                f"{self.base_url}/calc/{endpoint}",
                json=json,
                timeout=5,
            )

        if response.status_code == 400 and "detail" in response.json() and "Error" in response.json()["detail"]:
            return response.json()["detail"]['Error']

        if response.status_code != 200:
            self.logger.error("Error while making POST request. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")


        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", self.data)
        return ""

    def delete(self, endpoint, params=None):
        if params is None:
            params = {}

        response = requests.delete(
                f"{self.base_url}/calc/{endpoint}",
                timeout=5,
                params=params,
            )

        if response.status_code != 200:
            self.logger.error("Error while deleting variable. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")

        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", self.data)

    def save_state(self, session_id):
        """ Ещё один специальный post-запрос для сохранения в файл """
        response = requests.post(
                f"{self.base_url}/calc/save_state",
                params={"session_id": session_id},
                timeout=5,
            )

        if response.status_code != 200:
            self.logger.error("Error while saving sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")

