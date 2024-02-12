# File Storage

![](https://img.shields.io/badge/pydantic-2.4.2-blue)
![](https://img.shields.io/badge/SQLAlchemy-2.0.21-white)
![](https://img.shields.io/badge/fastapi-0.109.2-turquoise)
![](https://img.shields.io/badge/alembic-1.12.0-red)

![](https://img.shields.io/badge/black-23.10.1-black)
![](https://img.shields.io/badge/flake8-6.1.0-blue)
![](https://img.shields.io/badge/isort-5.12.0-grey)


File Storage - это сервер для хранения файлов с функционалом загрузки, получения метаинформации, скачивания и удаления файлов. Он предоставляет простой API для работы с файлами и хранит метаданные файлов в базе данных PostgreSQL. Аналогично Amazon S3, FileStorage поддерживает заголовки и метаданные файлов, однако отличается тем, что может быть развернут как локальный сервер, что делает его более доступным для небольших проектов или локальных применений.

### Функциональные требования

Подробное описание представлено в [Техническом Задании](https://github.com/semyonnakrokhin/file_storage/blob/main/%D0%A2%D0%97.pdf)
1. Загрузка файлов: Пользователи могут загружать файлы на сервер с помощью API запроса POST /api/upload. При загрузке файлов пользователи могут указать идентификатор, имя и тег файла.
2. Получение метаданных файлов: Сервер предоставляет API запрос GET /api/get для получения метаданных файлов. Пользователи могут фильтровать файлы по различным критериям, таким как идентификатор, имя и тег файла.
3. Удаление файлов: Сервер позволяет удалить файлы с помощью API запроса DELETE /api/delete. Пользователи могут указать критерии для удаления файлов, и сервер удалит файлы, соответствующие этим критериям.
4. Скачивание файлов: Пользователи могут скачать файлы с сервера с помощью API запроса GET /api/download, указав идентификатор файла.


### Конфигурация и запуск приложения

[В процессе]

Наглядно процесс конфигурации и запуска приложения представлен на рисунке ниже:

![Конфигурация и запуск](uml/images/configuration_start.drawio.png)

В файле .env содержится:

  - Параметры подключения к базе данных

В файле .env.test содержатся параметры подключения к тестовой базе данных

В файле .env.postgres содержатся параметры бд для поднятия контейнера с PostgreSQL

Конкретные именя переменных, опций и разделов можно найти в файле [environment.txt](https://github.com/semyonnakrokhin/weather_collector/blob/main/environment.txt)

### Общая архитектура приложения

[В процессе]

![Общая архитектура](uml/images/weather_collector.drawio.png)

Над каждым классом указана модель данных, с которой данный класс работает.
За преобразование одной модели в другую отвечают мапперы.

### Модели и преобразование моделей

Информация о составе моделей приложения и логике их преобразования представлена на диаграме ниже. В ней также представлены, какие атрибуты входят в каждый объект одного из указанных типов. Белым шрифтом в цветных прямоугольниках указаны области применения данных моделей:

![Модели](uml/images/models.drawio.png)

[В процессе]


# Запуск в контейнерах Docker
1. Перейдите в директорию с вашими проектами.
2. Склонируйте репозиторий на свой локальный компьютер:

```shell
# Linux
> https://github.com/semyonnakrokhin/file_storage.git
```

3. Перейдите в каталог проекта:

```shell
# Linux
> cd file_storage
```

4. В этой директории создайте файлы, перечисленные в [environment.txt](https://github.com/semyonnakrokhin/weather_collector/blob/main/environment.txt)

5. Выполните команду находясь в корневой директории проекта:

```shell
# Linux
> docker-compose up --build
```

6. Для остановки контейнеров выполните команду:

```shell
# Linux
> docker-compose down
```

# Вклад
Если вы хотите внести свой вклад в проект File Storge, пожалуйста, ознакомьтесь с CONTRIBUTING.md для получения дополнительной информации о том, как начать.

# Авторы
Семен Накрохин
2206095@gmail.com

# Лицензия
Этот проект распространяется под лицензией MIT. Подробности смотрите в файле LICENSE.
