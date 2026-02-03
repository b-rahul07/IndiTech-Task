from django.contrib import admin
from .models import Clinic, UserProfile, FollowUp, PublicViewLog


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic_code', 'created_at')
    readonly_fields = ('clinic_code', 'created_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinic')
    search_fields = ('user__username',)


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'clinic',
        'status',
        'due_date',
        'language',
        'created_at',
    )
    list_filter = ('status', 'language', 'clinic')
    search_fields = ('patient_name', 'phone')
    readonly_fields = ('public_token', 'created_at', 'updated_at')


@admin.register(PublicViewLog)
class PublicViewLogAdmin(admin.ModelAdmin):
    list_display = ('followup', 'viewed_at', 'ip_address')
    readonly_fields = ('viewed_at',)
