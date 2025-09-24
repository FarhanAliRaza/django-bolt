#!/usr/bin/env python
"""
Script to run Django with Uvicorn ASGI server for high performance.
Supports multiple workers and various configuration options.
"""

import argparse
import os
import sys
import uvicorn
from multiprocessing import cpu_count


def main():
    parser = argparse.ArgumentParser(description='Run Django with Uvicorn ASGI server')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Bind socket to this host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Bind socket to this port (default: 8000)')
    parser.add_argument('--workers', type=int, default=1,
                        help='Number of worker processes (default: 1)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload on code changes')
    parser.add_argument('--log-level', type=str, default='info',
                        choices=['critical', 'error', 'warning', 'info', 'debug', 'trace'],
                        help='Set the log level (default: info)')
    parser.add_argument('--access-log', action='store_true',
                        help='Enable access log')
    parser.add_argument('--loop', type=str, default='auto',
                        choices=['auto', 'asyncio', 'uvloop'],
                        help='Event loop implementation (default: auto)')
    parser.add_argument('--http', type=str, default='auto',
                        choices=['auto', 'h11', 'httptools'],
                        help='HTTP protocol implementation (default: auto)')
    parser.add_argument('--ws', type=str, default='auto',
                        choices=['auto', 'none', 'websockets', 'wsproto'],
                        help='WebSocket protocol implementation (default: auto)')
    parser.add_argument('--lifespan', type=str, default='on',
                        choices=['auto', 'on', 'off'],
                        help='Lifespan protocol (default: on)')
    parser.add_argument('--limit-concurrency', type=int, default=None,
                        help='Maximum number of concurrent connections')
    parser.add_argument('--limit-max-requests', type=int, default=None,
                        help='Maximum number of requests to serve before restarting workers')
    parser.add_argument('--timeout-keep-alive', type=int, default=5,
                        help='Keep-alive timeout in seconds (default: 5)')
    
    args = parser.parse_args()
    
    # Set Django settings module if not already set
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testproject.settings')
    
    # Import Django and setup
    import django
    django.setup()
    
    # Configure uvicorn
    config = {
        'app': 'testproject.asgi:application',
        'host': args.host,
        'port': args.port,
        'workers': args.workers,
        'reload': args.reload,
        'log_level': args.log_level,
        'access_log': args.access_log,
        'loop': args.loop,
        'http': args.http,
        'ws': args.ws,
        'lifespan': args.lifespan,
    }
    
    # Add optional parameters if specified
    if args.limit_concurrency:
        config['limit_concurrency'] = args.limit_concurrency
    if args.limit_max_requests:
        config['limit_max_requests'] = args.limit_max_requests
    if args.timeout_keep_alive:
        config['timeout_keep_alive'] = args.timeout_keep_alive
    
    # Print startup information
    print(f"Starting Uvicorn ASGI server...")
    print(f"Host: {args.host}:{args.port}")
    print(f"Workers: {args.workers}")
    print(f"Reload: {args.reload}")
    print(f"Log level: {args.log_level}")
    print(f"HTTP implementation: {args.http}")
    print(f"Event loop: {args.loop}")
    
    # Run uvicorn
    uvicorn.run(**config)


if __name__ == '__main__':
    main()