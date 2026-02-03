from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

from .models import Clinic, FollowUp, PublicViewLog, UserProfile


class FollowUpTests(TestCase):

    def setUp(self):
        # Clinics
        self.clinic_a = Clinic.objects.create(name="Clinic A")
        self.clinic_b = Clinic.objects.create(name="Clinic B")

        # Users
        self.user_a = User.objects.create_user(
            username="usera", password="pass123"
        )
        self.user_b = User.objects.create_user(
            username="userb", password="pass123"
        )

        # Create UserProfiles explicitly
        UserProfile.objects.create(user=self.user_a, clinic=self.clinic_a)
        UserProfile.objects.create(user=self.user_b, clinic=self.clinic_b)

        # Followup for clinic A
        self.followup = FollowUp.objects.create(
            clinic=self.clinic_a,
            created_by=self.user_a,
            patient_name="Test Patient",
            phone="9999999999",
            due_date=date.today(),
        )

        self.client = Client()

    def test_clinic_code_is_unique(self):
        clinic_codes = Clinic.objects.values_list("clinic_code", flat=True)
        self.assertEqual(len(clinic_codes), len(set(clinic_codes)))

    def test_public_token_is_unique(self):
        tokens = FollowUp.objects.values_list("public_token", flat=True)
        self.assertEqual(len(tokens), len(set(tokens)))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_cross_clinic_access_blocked(self):
        self.client.login(username="userb", password="pass123")
        response = self.client.get(reverse("dashboard"))
        self.assertNotContains(response, "Test Patient")

    def test_public_page_creates_view_log(self):
        initial_count = PublicViewLog.objects.count()
        self.client.get(reverse("public_followup", args=[self.followup.public_token]))
        self.assertEqual(
            PublicViewLog.objects.count(),
            initial_count + 1
        )
