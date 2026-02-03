from django.db import models
from django.contrib.auth.models import User
import secrets


class Clinic(models.Model):
    name = models.CharField(max_length=255)

    clinic_code = models.CharField(
        max_length=16,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.clinic_code:
            self.clinic_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        return secrets.token_urlsafe(8)

    def __str__(self):
        return f"{self.name} ({self.clinic_code})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='users'
    )

    def __str__(self):
        return f"{self.user.username} - {self.clinic.name}"


class FollowUp(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_DONE, 'Done'),
    ]

    LANGUAGE_EN = 'en'
    LANGUAGE_HI = 'hi'

    LANGUAGE_CHOICES = [
        (LANGUAGE_EN, 'English'),
        (LANGUAGE_HI, 'Hindi'),
    ]

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='followups'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_followups'
    )

    patient_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default=LANGUAGE_EN
    )

    notes = models.TextField(blank=True)

    due_date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    public_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = self.generate_public_token()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_public_token():
        return secrets.token_urlsafe(16)

    def __str__(self):
        return f"{self.patient_name} ({self.status})"

class PublicViewLog(models.Model):
    followup = models.ForeignKey(
        FollowUp,
        on_delete=models.CASCADE,
        related_name='view_logs'
    )

    viewed_at = models.DateTimeField(auto_now_add=True)

    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"View of {self.followup_id} at {self.viewed_at}"
