import importlib
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps

from django_bolt.api import BoltAPI
from django_bolt import _core


class Command(BaseCommand):
    help = "Run Django-Bolt server with autodiscovered APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0)"
        )
        parser.add_argument(
            "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
        )
        parser.add_argument(
            "--processes", type=int, default=1, help="Number of processes (default: 1)"
        )
        parser.add_argument(
            "--workers", type=int, default=2, help="Workers per process (default: 2)"
        )
        parser.add_argument(
            "--admin-mode",
            choices=["off", "wsgi", "asgi"],
            default="off",
            help="Admin integration mode (default: off)",
        )
        parser.add_argument(
            "--dev",
            action="store_true",
            help="Enable auto-reload on file changes (development mode)"
        )

    def handle(self, *args, **options):
        processes = options['processes']
        dev_mode = options.get('dev', False)

        # Dev mode: force single process + single worker + enable auto-reload
        if dev_mode:
            options['workers'] = 1
            if processes > 1:
                self.stdout.write(
                    self.style.WARNING(
                        "[django-bolt] Dev mode enabled: forcing --processes=1 for auto-reload"
                    )
                )
                options['processes'] = 1

            self.stdout.write(
                self.style.SUCCESS("[django-bolt] 🔥 Development mode enabled (auto-reload on file changes)")
            )
            self.run_with_autoreload(options)
        else:
            # Production mode (current logic)
            if processes > 1:
                self.start_multiprocess(options)
            else:
                self.start_single_process(options)

    def run_with_autoreload(self, options):
        """Run server with auto-reload using watchfiles"""
        import sys
        import os
        import signal
        import subprocess
        from pathlib import Path

        try:
            from watchfiles import watch
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "[django-bolt] Error: watchfiles not installed. "
                    "Install it with: pip install watchfiles"
                )
            )
            sys.exit(1)

        # Watch paths - Django project base directory
        watch_path = Path(settings.BASE_DIR)

        self.stdout.write(f"[django-bolt] Watching for changes in: {watch_path}")
        self.stdout.write("[django-bolt] Press Ctrl+C to quit\n")

        # Keep track of server process
        server_process = None

        def start_server_subprocess():
            """Start server in subprocess"""
            nonlocal server_process

            # Build command to restart ourselves without --dev
            cmd = [
                sys.executable,
                "manage.py",
                "runbolt",
                "--host", options['host'],
                "--port", str(options['port']),
                "--workers", str(options['workers']),
            ]

            server_process = subprocess.Popen(
                cmd,
                cwd=settings.BASE_DIR,
                env=os.environ.copy(),
            )
            return server_process

        def stop_server():
            """Stop server subprocess"""
            nonlocal server_process
            if server_process and server_process.poll() is None:
                server_process.terminate()
                try:
                    server_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    server_process.kill()
                    server_process.wait()

        # Handle Ctrl+C
        def signal_handler(signum, frame):
            stop_server()
            self.stdout.write("\n[django-bolt] Shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start initial server
        start_server_subprocess()

        # Watch for changes
        try:
            for changes in watch(watch_path, watch_filter=lambda change, path: path.endswith('.py'), debounce=300):
                if changes:
                    # Get first changed file for display
                    change_type, changed_file = list(changes)[0]
                    rel_path = Path(changed_file).relative_to(watch_path)
                    self.stdout.write(f"[django-bolt] 🔄 File changed: {rel_path} - Reloading...")

                    # Stop and restart server
                    stop_server()
                    start_server_subprocess()
        except KeyboardInterrupt:
            stop_server()
            self.stdout.write("\n[django-bolt] Shutting down...")

    def start_multiprocess(self, options):
        """Start multiple processes with SO_REUSEPORT"""
        import os
        import sys
        import signal
        
        processes = options['processes']
        self.stdout.write(f"[django-bolt] Starting {processes} processes with SO_REUSEPORT")
        
        # Store child PIDs for cleanup
        child_pids = []
        
        def signal_handler(signum, frame):
            self.stdout.write("\n[django-bolt] Shutting down processes...")
            for pid in child_pids:
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Fork processes
        for i in range(processes):
            pid = os.fork()
            if pid == 0:
                # Child process
                os.environ['DJANGO_BOLT_REUSE_PORT'] = '1'
                os.environ['DJANGO_BOLT_PROCESS_ID'] = str(i)
                self.start_single_process(options, process_id=i)
                sys.exit(0)
            else:
                # Parent process
                child_pids.append(pid)
                self.stdout.write(f"[django-bolt] Started process {i} (PID: {pid})")
        
        # Parent waits for children
        try:
            while True:
                pid, status = os.wait()
                self.stdout.write(f"[django-bolt] Process {pid} exited with status {status}")
                if pid in child_pids:
                    child_pids.remove(pid)
                if not child_pids:
                    break
        except KeyboardInterrupt:
            pass
    
    def start_single_process(self, options, process_id=None):
        """Start a single process server"""
        if process_id is not None:
            self.stdout.write(f"[django-bolt] Process {process_id}: Starting autodiscovery...")
        else:
            self.stdout.write("[django-bolt] Starting autodiscovery...")
        
        # Autodiscover BoltAPI instances
        apis = self.autodiscover_apis()
        
        if not apis:
            self.stdout.write(
                self.style.WARNING("No BoltAPI instances found. Create api.py files with api = BoltAPI()")
            )
            return
        
        # Merge all APIs and collect routes
        merged_api = self.merge_apis(apis)
        
        if process_id is not None:
            self.stdout.write(f"[django-bolt] Process {process_id}: Found {len(merged_api._routes)} routes from {len(apis)} APIs")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"[django-bolt] Found {len(merged_api._routes)} routes")
            )
        
        # Register routes with Rust
        rust_routes = []
        for method, path, handler_id, handler in merged_api._routes:
            # Ensure matchit path syntax
            from django_bolt.api import BoltAPI
            convert = getattr(merged_api, "_convert_path", None)
            norm_path = convert(path) if callable(convert) else path
            rust_routes.append((method, norm_path, handler_id, handler))

        _core.register_routes(rust_routes)

        # Register middleware metadata if present
        if merged_api._handler_middleware:
            middleware_data = [
                (handler_id, meta)
                for handler_id, meta in merged_api._handler_middleware.items()
            ]
            _core.register_middleware_metadata(middleware_data)
            if process_id is not None:
                self.stdout.write(f"[django-bolt] Process {process_id}: Registered middleware for {len(middleware_data)} handlers")
            else:
                self.stdout.write(f"[django-bolt] Registered middleware for {len(middleware_data)} handlers")
        
        if process_id is not None:
            self.stdout.write(f"[django-bolt] Process {process_id}: Starting server on http://{options['host']}:{options['port']}")
            self.stdout.write(f"[django-bolt] Process {process_id}: Workers: {options['workers']}")
        else:
            self.stdout.write(f"[django-bolt] Starting server on http://{options['host']}:{options['port']}")
            self.stdout.write(f"[django-bolt] Workers: {options['workers']}, Processes: {options['processes']}")
        
        # Set environment variable for Rust to read worker count
        import os
        os.environ['DJANGO_BOLT_WORKERS'] = str(options['workers'])
        
        # Start the server
        _core.start_server_async(merged_api._dispatch, options["host"], options["port"])

    def autodiscover_apis(self):
        """Discover BoltAPI instances from installed apps"""
        apis = []
        
        # Check explicit settings first
        if hasattr(settings, 'BOLT_API'):
            for api_path in settings.BOLT_API:
                api = self.import_api(api_path)
                if api:
                    apis.append((api_path, api))
            return apis
        
        # Try project-level API first (common pattern)
        project_name = settings.ROOT_URLCONF.split('.')[0]  # Extract project name from ROOT_URLCONF
        project_candidates = [
            f"{project_name}.api:api",
            f"{project_name}.bolt_api:api",
        ]
        
        for candidate in project_candidates:
            api = self.import_api(candidate)
            if api:
                apis.append((candidate, api))
        
        # Autodiscover from installed apps
        for app_config in apps.get_app_configs():
            # Skip django_bolt itself
            if app_config.name == 'django_bolt':
                continue
                
            # Check if app config has bolt_api hint
            if hasattr(app_config, 'bolt_api'):
                api = self.import_api(app_config.bolt_api)
                if api:
                    apis.append((app_config.bolt_api, api))
                continue
            
            # Try standard locations
            app_name = app_config.name
            candidates = [
                f"{app_name}.api:api",
                f"{app_name}.bolt_api:api",
            ]
            
            for candidate in candidates:
                api = self.import_api(candidate)
                if api:
                    apis.append((candidate, api))
                    break  # Only take first match per app
        
        return apis

    def import_api(self, dotted_path):
        """Import a BoltAPI instance from dotted path like 'myapp.api:api'"""
        try:
            if ':' not in dotted_path:
                return None
            
            module_path, attr_name = dotted_path.split(':', 1)
            module = importlib.import_module(module_path)
            
            if not hasattr(module, attr_name):
                return None
            
            api = getattr(module, attr_name)
            
            # Verify it's a BoltAPI instance
            if isinstance(api, BoltAPI):
                return api
            
        except (ImportError, AttributeError, ValueError):
            pass
        
        return None

    def merge_apis(self, apis):
        """Merge multiple BoltAPI instances into one"""
        if len(apis) == 1:
            return apis[0][1]  # Return the single API

        # Create a new merged API
        merged = BoltAPI()
        route_map = {}  # Track conflicts

        for api_path, api in apis:
            self.stdout.write(f"[django-bolt] Merging API from {api_path}")

            for method, path, handler_id, handler in api._routes:
                route_key = f"{method} {path}"

                if route_key in route_map:
                    raise CommandError(
                        f"Route conflict: {route_key} defined in both "
                        f"{route_map[route_key]} and {api_path}"
                    )

                route_map[route_key] = api_path
                merged._routes.append((method, path, handler_id, handler))
                merged._handlers[handler_id] = handler

                # Merge handler metadata
                if handler in api._handler_meta:
                    merged._handler_meta[handler] = api._handler_meta[handler]

                # Merge middleware metadata
                if handler_id in api._handler_middleware:
                    merged._handler_middleware[handler_id] = api._handler_middleware[handler_id]

        # Update next handler ID
        if merged._routes:
            merged._next_handler_id = max(h_id for _, _, h_id, _ in merged._routes) + 1

        return merged
