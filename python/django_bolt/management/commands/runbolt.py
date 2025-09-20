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
            "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
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

    def handle(self, *args, **options):
        processes = options['processes']
        
        if processes > 1:
            self.start_multiprocess(options)
        else:
            self.start_single_process(options)
    
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
                self.style.SUCCESS(f"[django-bolt] Found {len(merged_api._routes)} routes from {len(apis)} APIs")
            )
        
        # Register routes with Rust
        rust_routes = [
            (method, path, handler_id, handler)
            for method, path, handler_id, handler in merged_api._routes
        ]
        
        _core.register_routes(rust_routes)
        
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
        
        # Update next handler ID
        if merged._routes:
            merged._next_handler_id = max(h_id for _, _, h_id, _ in merged._routes) + 1
        
        return merged
