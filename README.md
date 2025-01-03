# OPPA Python 3.9

Инструкция по поднятию проекта
Первым делом нужно создать .env файл, в той же директории, в которой лежит 
env.example. Копируем ключи из env.example и заполняем данные.

По важным ключам: (Также можете на проде посмотреть файл .env)

`POSTGRES_DB` `POSTGRES_USER` `POSTGRES_PASSWORD` автоматически проставляются в
docker postgres. То есть создаете docker с postgres, и эти значения из файла 
.env перетянутся в сам postgres внутри docker

Все поля по NIKITA берете из личного кабинета NIKITA.
`NIKITA_TEST` = 1 (true) либо 0 (false)
`FIREBASE_APPLICATION_CREDENTIALS` = скачивайте из Firebase
этот json файл с cred и указывайте путь до него. Лучше положить его в папку main

Все данные по PAYBOX берете из личного кабинета PAYBOX.
`PAYBOX_RESULT_URL` = ставите либо true, либо false



## Docker

В папке с файлом docker-compose введите команду ниже. Весь проект поднимается сам. 
Далее пройдите по localhost:8000. Сервер поднимается с помощью gunicorn.


PROD
```bash
docker-compose up -d
```
LOCAL (без nginx)
```bash
docker-compose up -d backend celery_worker celery_beat database redis
```
CERTBOT
```bash
sudo ./init-letsencrypt.sh
```
info https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71

## Локально

Я советую все зависимости (postgres, redis) поднять с помощью Docker. Но при
желании можете поднять у себя без Docker.
Для этого в .env файле вам нужно дать ключам значение 
`DB_HOST=localhost` `REDIS_HOST=localhost`. Ну имеется ввиду настроить docker-compose 
на внешние ключи. 

Далее нужно создать virtualenv. Скачать зависимости. Провести миграции

```bash
pip install -r requirements.txt
```
```bash
cd main
python manage.py migrate
python manage.py runserver
```

Тут нет никаких подводных камней. Самое просто развертывание
проекта
