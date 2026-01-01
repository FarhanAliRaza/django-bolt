---
icon: lucide/layers
---

# Deployment

This guide explains how to deploy Django-Bolt for production.

## Scaling with processes

Use `--processes` to scale your API. Each process runs a separate Python interpreter, bypassing the GIL limitation:

```bash
# 4 processes = 4 parallel Python executions
python manage.py runbolt --processes 4
```

Under the hood, Django-Bolt uses `SO_REUSEPORT` so the kernel load-balances incoming connections across all processes.

**Rule of thumb:** Set `--processes` to the number of CPU cores available.

## Production deployment

For production, run Django-Bolt as a managed service behind a reverse proxy.

### Running as a service

You need a process manager to keep Django-Bolt running. Choose systemd (most Linux distributions) or supervisor.

#### With systemd

Create `/etc/systemd/system/django-bolt.service`:

```ini
[Unit]
Description=Django-Bolt API Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/python manage.py runbolt --host 127.0.0.1 --port 8000 --processes 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable django-bolt
sudo systemctl start django-bolt
```

Check status:

```bash
sudo systemctl status django-bolt
```

#### With supervisor

Install supervisor and create `/etc/supervisor/conf.d/django-bolt.conf`:

```ini
[program:django-bolt]
command=/path/to/venv/bin/python manage.py runbolt --host 127.0.0.1 --port 8000 --processes 4
directory=/path/to/your/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django-bolt.log
```

Then reload and start:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start django-bolt
```

### Reverse proxy with nginx

Once the server is running, configure nginx to proxy requests to it:

```nginx
upstream django_bolt {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://django_bolt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test and reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Performance tuning

### Socket backlog

For high-traffic servers, increase the socket backlog:

```bash
python manage.py runbolt --processes 4 --backlog 2048
```

### Keep-alive timeout

Adjust HTTP keep-alive timeout (useful for long-lived connections):

```bash
python manage.py runbolt --processes 4 --keep-alive 30
```

### Compression

Enable compression for smaller response sizes:

```python
# settings.py
from django_bolt.middleware import CompressionConfig

BOLT_COMPRESSION = CompressionConfig(
    backend="gzip",
    minimum_size=500,  # Only compress responses > 500 bytes
)
```

## Workers vs Processes

You might wonder about Actix's worker threads. Django-Bolt uses 1 worker per process by default because **Python's GIL is the bottleneck**, not Rust.

Workers are threads within a single process. Due to Python's Global Interpreter Lock, only one thread can execute Python code at a time. More workers just means more threads waiting:

```
Process with 4 workers:
├── Worker 0: [waiting for GIL]
├── Worker 1: [waiting for GIL]
├── Worker 2: [executing Python handler] ← only one runs
└── Worker 3: [waiting for GIL]
```

The Rust parts (HTTP parsing, routing, compression) take microseconds. Your Python handler takes milliseconds. You won't saturate the Rust side.

**Use processes for parallelism**, not workers. Each process has its own GIL, enabling true parallel execution.

If you still want to increase workers, set the environment variable:

```bash
DJANGO_BOLT_WORKERS=2 python manage.py runbolt --processes 4
```
