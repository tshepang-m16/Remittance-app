from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .services import (
    ForLearning as learning_service,
    budget as budget_service,
    dashboard as dashboard_service,
    donate as donate_service,
    login as login_service,
    profile as profile_service,
    promotions as promotions_service,
    users as users_service,
)


NAVIGATION_PAGES = {
    "dashboard": "dashboard.html",
    "login": "login.html",
    "logout": "logout.html",
    "promotions": "promotions.html",
    "budget": "budget.html",
    "donate": "donate.html",
    "profile": "profile.html",
    "learning": "ForLearning.html",
    "users": "users.html",
}


def render_page(request: HttpRequest, template_name: str, active_page: str, context: dict | None = None) -> HttpResponse:
    context = context or {}
    context.setdefault("active_page", active_page)
    return render(request, template_name, context)


def dashboard_view(request: HttpRequest) -> HttpResponse:
    success, extras = dashboard_service.handle_post(request, request.user)
    if success:
        messages.success(request, "Dashboard updated successfully.")
        return redirect("dashboard")
    context = dashboard_service.build_context(request.user, overrides=extras)
    return render_page(request, NAVIGATION_PAGES["dashboard"], "dashboard", context)


def login_view(request: HttpRequest) -> HttpResponse:
    success, form = login_service.handle_request(request)
    if success:
        messages.success(request, "Welcome back!")
        next_url = request.GET.get("next") or reverse("dashboard")
        return redirect(next_url)
    context = login_service.build_context(form)
    return render_page(request, NAVIGATION_PAGES["login"], "login", context)


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect("login")
    return render_page(request, NAVIGATION_PAGES["logout"], "logout")


def promotions_view(request: HttpRequest) -> HttpResponse:
    promotions = promotions_service.list_promotions()
    context = {"promotions": promotions}
    return render_page(request, NAVIGATION_PAGES["promotions"], "promotions", context)


def budget_view(request: HttpRequest) -> HttpResponse:
    success, extras = budget_service.handle_post(request, request.user)
    if success:
        messages.success(request, "Budget entry saved.")
        return redirect("budget")
    context = budget_service.build_context(
        request.user,
        month=request.GET.get("month"),
    )
    context.update(extras)
    return render_page(request, NAVIGATION_PAGES["budget"], "budget", context)


def donate_view(request: HttpRequest) -> HttpResponse:
    success, extras = donate_service.handle_post(request, request.user)
    if success:
        messages.success(request, "Thank you for your donation!")
        return redirect("donate")
    context = donate_service.build_context(request.user)
    context.update(extras)
    return render_page(request, NAVIGATION_PAGES["donate"], "donate", context)


def profile_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        messages.info(request, "Please sign in to manage your profile.")
        return redirect("login")

    context = profile_service.build_context(request.user)

    if request.method == "POST":
        success, form = profile_service.handle_post(request, request.user)
        if success:
            messages.success(request, "Profile updated.")
            return redirect("profile")
        context["form"] = form

    return render_page(request, NAVIGATION_PAGES["profile"], "profile", context)


def learning_view(request: HttpRequest) -> HttpResponse:
    category = request.GET.get("category")
    resources = learning_service.list_resources(category)
    counts = learning_service.category_counts()
    context = {
        "resources": resources,
        "category_counts": counts,
        "selected_category": category or "all",
    }
    return render_page(request, NAVIGATION_PAGES["learning"], "learning", context)


def users_view(request: HttpRequest) -> HttpResponse:
    context = {
        "total_users": users_service.total_users(),
        "membership_breakdown": users_service.category_breakdown(),
    }
    return render_page(request, NAVIGATION_PAGES["users"], "users", context)
