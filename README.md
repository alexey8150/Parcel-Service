1. Install dependencies:

```
pipenv install
pipenv shell
```
2.cp example.env .env:

3.Up docker-compose:
```
docker-compose up -d --build
docker-compose down (to disable after work)
```
4.Create database schema:
```
docker-compose exec app aerich init -t src.storage_conf.database.TORTOISE_ORM
```
5. On http:localhost:8080/docs# - you can see the API's documentation.
6. To start a periodic task immediately:
```
celery -A src.tasks.celery_app worker --loglevel=info
celery -A src.tasks.celery_app call src.celery_app.<task_name>
```
