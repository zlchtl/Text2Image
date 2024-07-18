# Text2Image - генератор картинок в командной строке

Скрипт для генерации изображений через API [fusionbrain.ai](https://fusionbrain.ai)  
Для работы требуются личные **api_key** и **secret_key** в виртуальном окружении [Документация по ключам](https://fusionbrain.ai/docs/doc/poshagovaya-instrukciya-po-upravleniu-api-kluchami/)
Пример .env файла находится в examples  
Логи скрипта находятся в log
---

Запуск скрипта из консоли:  
```Bash
python .\main.py -p='Пушистый кот в очках' -st='реализм' -sh=1
```
## Флаги
* **prompt** — (**-p**, **--prompt**) текст запроса *(type = str; default='Кот в очках';)*  
* **width** — (**--width**) ширина *(type=int; default=1024);)*  
* **height** — (**--height**) высота *(type=int; default=1024);)*  
* **style** — (**-st**, **--style**) стиль изображения *(type=str; default='');)*  
* **ngprompt** — (**-np**, **--ngprompt**) текст негативного запроса *(type=str; default='');)*  
* **show** — (**-sh**, **--show**) показать результат *(type=bool; default=False);)*  
* **save** — (**-s**, **--save**) сохранить результат в файл *(type=bool; default=True);)*  
* **debug** — (**-db**, **--debug**) режим отладки *(type=bool; default=False);)*  
