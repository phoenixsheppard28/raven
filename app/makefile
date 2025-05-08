
celery:
	poetry run celery -A tasks worker --loglevel=ERROR 

redis:
	brew services start redis 

stop_redis:
	brew services stop redis

run:
	poetry run uvicorn main:app --reload

reset_db:
	poetry run python3 -m internal.db_setup

celery_scale:
	poetry run celery -A tasks worker --loglevel=info --concurrency=8

