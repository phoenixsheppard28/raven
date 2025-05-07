celery:
	poetry run celery -A tasks worker --loglevel=info

redis:
	brew services start redis 

stop_redis:
	brew services stop redis

run:
	poetry run uvicorn main:app --reload

drop_db:
	rm -r database.db 