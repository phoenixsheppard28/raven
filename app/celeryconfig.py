from app.internal.secrets import settings

# Broker Settings
broker_url = settings.REDIS_URL

# Task Settings
worker_max_tasks_per_child = 1
worker_concurrency = 8  # change to 24 to scale
worker_loglevel = 'info'

# Task Result Settings
task_track_started = True
task_time_limit = 480  # 8 minute hard time limit 
task_soft_time_limit = 240  # 4 minute soft time limit