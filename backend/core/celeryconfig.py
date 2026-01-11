# Broker & backend
broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"

# Serialization
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

# Timezone
timezone = "UTC"
enable_utc = True

# Task behavior
task_acks_late = True
task_reject_on_worker_lost = True
worker_prefetch_multiplier = 1

# Retry defaults
task_default_retry_delay = 30
task_max_retries = 5
