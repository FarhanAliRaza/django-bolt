import multiprocessing

# Gunicorn configuration for Django ASGI
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
timeout = 30

# Performance optimizations
preload_app = True
reuse_port = True

# Uvicorn worker settings
forwarded_allow_ips = "*"
accesslog = "-"
errorlog = "-"
loglevel = "error"

# Additional settings for the UvicornWorker
worker_tmp_dir = "/dev/shm"