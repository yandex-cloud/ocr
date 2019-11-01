Здесь содержится датасет и скрипты для воспроизведения результатов, упоминаемых в статье LINK_TO_ARTICLE.

Датасет содержит набор изображений, содержащих русскоязычный текст in the wild, включающий в себя: фотографии вывесок, объявлений, табличек, обложек книг, тексты на бытовых приборах, одежде и предметах.

В качество метрики для сравнения мы использовали стандартную метрику точности и полноты распознавания слов в датасете, а также F-меру. Распознанное слово считается правильно найденным, если его координаты соответствуют координатам размеченного слова (IoU > 0.3) и распознавание совпадает с размеченным с точностью до регистра. 


Для воспроизведения результатов ABBYY Cloud OCR SDK:
1. Получить Application ID (ID) и пароль (PSW) для ABBYY Cloud OCR SDK (https://cloud.ocrsdk.com)
2. Скачать `process.py` и `AbbyyOnlineSdk.py` из официального примера https://github.com/abbyysdk/ocrsdk.com/tree/master/Python
3. `python ocr_abbyy.py  --in_folder rus_ocr_in_the_wild_dataset --out_folder rus_ocr_in_the_wild_dataset_a --psw PSW --id ID`


Для воспроизведения результатов Google Cloud Vision API:
1. Получить ключ (APIKEY) для Google Cloud Vision API (https://console.cloud.google.com)
2. `python ocr_google.py  --in_folder rus_ocr_in_the_wild_dataset --out_folder rus_ocr_in_the_wild_dataset_g --key <APIKEY>`


Для воспроизведения результатов Yandex Vision:
1. Получить ключ (APIKEY) для Yandex Vision (https://console.cloud.yandex.ru/)
2. `python ocr_yandex.py  --in_folder rus_ocr_in_the_wild_dataset --out_folder rus_ocr_in_the_wild_dataset_y --key <APIKEY>`


Для подсчета метрики по полученным результатам:
```
python metrics.py rus_ocr_in_the_wild_dataset rus_ocr_in_the_wild_dataset_a
python metrics.py rus_ocr_in_the_wild_dataset rus_ocr_in_the_wild_dataset_g
python metrics.py rus_ocr_in_the_wild_dataset rus_ocr_in_the_wild_dataset_y
```




