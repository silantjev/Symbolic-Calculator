import sys
import logging
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.logger import make_logger

class CalcClient:
    def __init__(self, base_url='http://127.0.0.1:8000', logger=None):
        self.base_url = base_url
        if logger is None:
            logger_name = self.__class__.__name__
            self.logger = make_logger(name=logger_name, file=False, console=False, level=logging.WARNING)
        else:
            self.logger = logger

        self.data = self.get("get_state", params = {"full": True})
        self.logger.info("CalcClient connected and loaded data %s", list(self.data))
    
    # Запросы
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
            self.logger.error("Error while getting full sate. Status code: %s. Details: %s", response.status_code, response.text)
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
            self.logger.error("Error while getting full sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")


        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", data)
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
            self.logger.error("Error while getting full sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")


        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", data)
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
            self.logger.error("Error while getting full sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")

        data = response.json()
        self.data.update(data)
        self.logger.debug("CalcClient updated data %s", data)

    # сеттеры
    def set_option(self, k, val):
        try:
            val = int(val)
            if val == self.data['options'][k]:
                self.logger.debug("Trying to set the same value %d to option %s", val, k)
                return True
            if val > 1:
                self.data['options'][k] = val
                error = self.put_state()
                if error:
                    self.logger.error("Error: %s", error)
                    return False
                self.logger.debug("Option %s set to value %d", k, val)
                return True
            self.logger.warning("Wrong value of %s. The value should be positive but %d is given", k, val)
        except TypeError:
            self.logger.warning("Wrong type of the value of %s. The type is %s, but int is needed", k, type(val))
        return False

    def set_new_expr(self, expr):
        error = self.post(endpoint="set_new_expr", json={"expr": expr})
        if error:
            self.logger.error("Error while setting new expression: %s", error)
        return error

    def set_se(self, expr) -> str:
        self.data['se'] = str(expr)
        self.put_state()
        error = self.put_state()
        if error:
            self.logger.error("Error: %s", error)
            return error
        self.logger.info("Sympy-expression set: se = %s", self.data['se'])
        return ""

    def set_expr(self, expr):
        self.data['expr'] = expr
        self.put_state() # no exception
        self.logger.info("New expression set: expr = %s", self.data['expr'])

    def set_sec(self, sec):
        self.data['sec'] = sec
        self.put_state() # no exception
        self.logger.info("Field 'sec' set: sec = %s", self.data['sec'])

    def set_value(self, var, expr):
        self.data['values'][var] = expr
        error = self.put_state()
        if error:
            self.logger.error("Error: %s", error)
            return error
        self.logger.info("Value of %s set to %s", var, self.data['value'][var])
        return ""

    def delete_all_values(self):
        self.delete(endpoint="delete_all_values")
        self.logger.info("Values of all variables deleted")

    def delete_value(self, var):
        self.delete(endpoint="delete_value", params={"var": var})
        self.logger.info("Values of variable %s deleted", var)

    # геттеры
    def get_nice(self):
        return self.data['nice']

    def get_expr(self):
        return self.data['expr']

    def get_sec(self):
        return self.data['sec']

    def get_se(self):
        return self.data['se']

    def get_var_names(self):
        return self.data['values'].keys()

    def get_options(self):
        return self.data['options']

    def get_help_text(self):
        return self.data['help_text']

    def get_explanations(self):
        return self.data['explanations']

    def get_variables(self, include_unset=True):
        out_json = self.get(endpoint="get_variables", params={"include_unset": include_unset})
        return out_json["current"], out_json['lines']

    def current_values(self):
        out_json = self.get(endpoint="current_values")
        return out_json["expr"]

    def evaluate(self):
        out_json = self.get(endpoint="evaluate")
        return out_json["expr"]

    def clear_all(self):
        self.delete(endpoint="clear_all")
        self.logger.info("State cleared")

    def save_state(self, session_id):
        response = requests.post(
                f"{self.base_url}/calc/save_state",
                params={"session_id": session_id},
                timeout=5,
            )

        if response.status_code != 200:
            self.logger.error("Error while getting full sate. Status code: %s. Details: %s", response.status_code, response.text)
            raise requests.HTTPError(f"Bad status code {response.status_code}: {response.json()}")


if __name__ == '__main__':
    logger = make_logger(name="console", file=True, console=True, level=logging.DEBUG)
    calc = CalcClient(logger=logger)
    calc.put_state()
