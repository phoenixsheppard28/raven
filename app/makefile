
celery:
	poetry run celery -A tasks worker 

redis:
	brew services start redis 

stop_redis:
	brew services stop redis

run:
	poetry run uvicorn main:app --reload

reset_db:
	poetry run python3 -m internal.db_setup



