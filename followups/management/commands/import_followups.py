import csv
import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from followups.models import FollowUp, UserProfile


class Command(BaseCommand):
    help = "Import follow-ups from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True, help="Path to CSV file")
        parser.add_argument("--username", required=True, help="Username to assign follow-ups to")

    def handle(self, *args, **options):
        csv_path = options["csv"]
        username = options["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR("User does not exist"))
            return

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    "UserProfile not found. Assign the user to a clinic before importing."
                )
            )
            return

        if not profile.clinic:
            self.stderr.write(
                self.style.ERROR(
                    "UserProfile has no clinic assigned."
                )
            )
            return

        clinic = profile.clinic

        created = 0
        skipped = 0

        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    patient_name = row.get("patient_name", "").strip()
                    phone_raw = row.get("phone", "").strip()
                    language = row.get("language", "en").strip()
                    due_date_raw = row.get("due_date", "").strip()
                    notes = row.get("notes", "").strip()

                    # Required fields
                    if not patient_name or not phone_raw or not due_date_raw:
                        skipped += 1
                        continue

                    # Phone validation (same rule as form)
                    digits = re.sub(r"\D", "", phone_raw)
                    if len(digits) not in (10, 12):
                        skipped += 1
                        continue

                    # Due date validation
                    due_date = datetime.strptime(due_date_raw, "%Y-%m-%d").date()

                    FollowUp.objects.create(
                        clinic=clinic,
                        created_by=user,
                        patient_name=patient_name,
                        phone=digits,
                        language=language,
                        due_date=due_date,
                        notes=notes,
                        status="pending",
                    )

                    created += 1

                except Exception:
                    skipped += 1
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed: {created} created, {skipped} skipped"
            )
        )
