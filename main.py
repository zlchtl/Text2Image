import os
import logging
from dotenv import load_dotenv
import json
import requests
import time
import base64
from PIL import Image
from io import BytesIO
import argparse


class Text2ImageAPI:
    def __init__(self, prompt: str, width: int, height: int, style: str, neg_prompt: str,
                 show: bool, save: bool, debug: bool):
        self.DEBUG = debug
        self.init_loger()
        self.init_env()
        self.init_settings()

        self.get_models()  # получение списка моделей
        self.availability_service(self.models[0])  # TODO сделать выбор моделей (проверка доступности модели)

        uuid = self.generate(prompt, style, neg_prompt, model=self.models[0], width=width, height=height)
        base64_string = self.check_generation(uuid)
        self.base64_to_image(base64_string, show=show, save=save)

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
        if data['status'] != 'ACTIVE':
            self.logger.error('Модель не активна')

    def generate(self, prompt: str, style: str, neg_prompt: str, model: dict, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}",
                "style": f'{style}',
                "negativePromptUnclip": f'{neg_prompt}'
            }
        }

        data = {
            'model_id': (None, model['id']),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + self.KEYS['RUN'], headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        self.logger.debug(data)
        self.logger.info(f'Генерация запущена под id: {data['uuid']}')
        return data['uuid']

    def check_generation(self, request_id, attempts=9, delay=10):
        while attempts > -1:
            self.logger.debug(f'Проверка генерации <{request_id}> осталось попыток {attempts}')
            response = requests.get(self.URL + self.KEYS['status'] + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                self.logger.info(f'Генерация <{request_id}> успешна\n'
                                 f'Время выполнения: {data['generationTime']}\n'
                                 f'Цензура: {data['censored']}')
                return data['images'][0]
            attempts -= 1
            time.sleep(delay)

    def base64_to_image(self, base64_string: str, show: bool = True, save: bool = True):
        if "data:image" in base64_string:
            base64_string = base64_string.split(",")[1]
        image_bytes = base64.b64decode(base64_string)
        image_stream = BytesIO(image_bytes)
        img = Image.open(image_stream)
        if show:
            img.show()
        if save:
            img.save("image.jpg")
        self.logger.info(f'Конвертация изображения прошла успешно')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Text2Image')
    parser.add_argument('-p', '--prompt', type=str, default='Кот в очках')
    parser.add_argument('--width', type=int, default=1024)
    parser.add_argument('--height', type=int, default=1024)
    parser.add_argument('-st', '--style', type=str, default='')
    parser.add_argument('-np', '--ngprompt', type=str, default='')
    parser.add_argument('-sh', '--show', type=bool, default=False)
    parser.add_argument('-s', '--save', type=bool, default=True)
    parser.add_argument('-db', '--debug', type=bool, default=False)
    args = parser.parse_args()
    Text2ImageAPI(args.prompt, args.width, args.height, args.style, args.ngprompt, args.show, args.save, args.debug)
