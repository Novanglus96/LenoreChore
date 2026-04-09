# yourapp/management/commands/load_demo_data.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
from api.models import (
    Area,
)


class Command(BaseCommand):
    help = "Load demo fixtures if this is the first time the app is run"

    def handle(self, *args, **options):
        if Area.objects.exists():
            self.stdout.write(
                self.style.NOTICE(
                    "Skipping demo fixtures: data already exists."
                )
            )
        else:
            self.stdout.write("Loading demo data...")
            call_command("loaddata", "demo.json")
            self.stdout.write(self.style.SUCCESS("Demo data loaded."))
