import re
from django import forms
from django.utils import timezone
from .models import FollowUp


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = [
            "patient_name",
            "phone",
            "due_date",
            "language",
            "status",
            "notes",
        ]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        digits = re.sub(r"\D", "", phone)

        # Accept:
        # - 10 digit local numbers
        # - 12 digit numbers with country code (e.g. +91XXXXXXXXXX)
        if len(digits) not in (10, 12):
            raise forms.ValidationError("Enter a valid phone number.")

        return phone

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]

        # Only enforce future dates on CREATE
        if not self.instance.pk and due_date < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")

        return due_date
