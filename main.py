import os
import logging
from dotenv import load_dotenv
import json
import requests
import time


class Text2ImageAPI:
    def __init__(self, debug: bool = False):
        self.DEBUG = debug
        self.init_loger()
        self.init_env()
        self.init_settings()

        self.get_models()  # получение списка моделей
        self.availability_service(self.models[0])  # проверка доступности модели

    def init_loger(self):
        self.logger = logging.getLogger(__name__)
        if self.DEBUG:
            self.logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(f"log/DEBUG {__name__}.log", mode='w', encoding="UTF-8")
        else:
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(f"log/{__name__}.log", mode='w', encoding="UTF-8")
        handler.setFormatter(logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s"))
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.debug(f"Инициализация логера")

    def init_env(self):
        self.logger.debug(f"Инициализация виртуального окружения")
        load_dotenv()
        self.api_key = os.getenv("api_key")
        self.secret_key = os.getenv("secret_key")

    def init_settings(self):
        with open('settings.json') as f:
            settings = json.load(f)
        self.URL = settings['URL']
        self.KEYS = settings['KEYS']
        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.api_key}',
            'X-Secret': f'Secret {self.secret_key}'
        }
        self.logger.debug(f"Инициализация настроек скрипта")

    def get_models(self):
        self.logger.debug(f"Получение списка моделей")
        response = requests.get(self.URL + self.KEYS["MODELS"], headers=self.AUTH_HEADERS)
        self.models = response.json()

    def availability_service(self, model: dict):
        param = {'model_id': (None, model['id'])}
        response = requests.get(self.URL + self.KEYS["availability"], headers=self.AUTH_HEADERS, files=param)
        data = response.json()
        self.logger.info(f'Статус модели <{model['name']} {model['version']}>: {data['status']}')


if __name__ == "__main__":
    generator = Text2ImageAPI(debug=True)
