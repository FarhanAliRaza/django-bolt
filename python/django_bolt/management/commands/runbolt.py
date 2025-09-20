from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start Django-Bolt development server"

    def add_arguments(self, parser):
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=8000)

    def handle(self, *args, **options):
        from django_bolt.bootstrap import ensure_django_ready
        from django_bolt.api import BoltAPI

        info = ensure_django_ready()
        self.stdout.write(
            self.style.SUCCESS(
                f"django-bolt: mode={info.get('mode')} db={info.get('database_name')}"
            )
        )

        api = BoltAPI()
        api.serve(options["host"], int(options["port"]))



