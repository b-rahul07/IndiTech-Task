# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import FollowUpForm
from .models import FollowUp, PublicViewLog, UserProfile


@login_required
def dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    clinic = profile.clinic

    followups = (
        FollowUp.objects
        .filter(clinic=clinic)
        .annotate(view_count=Count("view_logs"))
        .order_by("due_date")
    )

    status = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if status:
        followups = followups.filter(status=status)

    if start_date:
        followups = followups.filter(due_date__gte=start_date)

    if end_date:
        followups = followups.filter(due_date__lte=end_date)

    # Clinic-wide summary counts (before filtering)
    all_clinic_followups = FollowUp.objects.filter(clinic=clinic)
    total_count = all_clinic_followups.count()
    pending_count = all_clinic_followups.filter(status="pending").count()
    done_count = all_clinic_followups.filter(status="done").count()

    return render(
        request,
        "dashboard.html",
        {
            "followups": followups,
            "total_count": total_count,
            "pending_count": pending_count,
            "done_count": done_count,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
        },
    )


@login_required
def create_followup(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.clinic = profile.clinic
            followup.created_by = request.user
            followup.save()
            messages.success(request, "Follow-up created successfully.")
            return redirect("dashboard")
    else:
        form = FollowUpForm()

    return render(
        request,
        "followup_form.html",
        {
            "form": form,
            "title": "Create Follow-up",
        },
    )


@login_required
def edit_followup(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)
    followup = get_object_or_404(
        FollowUp,
        id=pk,
        clinic=profile.clinic,
    )

    if request.method == "POST":
        form = FollowUpForm(request.POST, instance=followup)
        if form.is_valid():
            form.save()
            messages.success(request, "Follow-up updated successfully.")
            return redirect("dashboard")
    else:
        form = FollowUpForm(instance=followup)

    return render(
        request,
        "followup_form.html",
        {
            "form": form,
            "title": "Edit Follow-up",
        },
    )


@login_required
@require_POST
def mark_done(request, pk):
    profile = get_object_or_404(UserProfile, user=request.user)

    followup = get_object_or_404(
        FollowUp,
        pk=pk,
        clinic=profile.clinic,
    )

    followup.status = "done"
    followup.save(update_fields=["status"])

    messages.success(request, "Follow-up marked as done.")
    return redirect("dashboard")


def public_followup(request, token):
    followup = get_object_or_404(FollowUp, public_token=token)

    PublicViewLog.objects.create(
        followup=followup,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        viewed_at=timezone.now(),
    )

    message = {
        "en": "Please contact the clinic for your follow-up.",
        "hi": "\u0915\u0943\u092a\u092f\u093e \u0905\u092a\u0928\u0940 \u092b\u0949\u0932\u094b-\u0905\u092a \u0915\u0947 \u0932\u093f\u090f \u0915\u094d\u0932\u093f\u0928\u093f\u0915 \u0906\u090f\u0902\u0964",
    }.get(followup.language, "Please contact the clinic.")

    return render(
        request,
        "public_followup.html",
        {
            "followup": followup,
            "message": message,
        },
    )
