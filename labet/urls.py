"""
URL configuration for LaBet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("game/<int:id>/", views.game_by_id, name="game_by_id"),
    path("wallet", views.wallet, name="wallet"),
    path("tier/", views.tier, name="tier"),
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.register, name="register"),
    path("betclic_test/", views.betclic_test, name="betclic_test"),
    path("placard_test/", views.placard_test, name="placard_test"),
    path("betano_test/", views.betano_test, name="betano_test"),
    path("lebull_test/", views.lebull_test, name="lebull_test"),
    path("combinations/", views.combinations, name="combinations"),
    path("combinations/<int:id>/", views.combinations_by_id, name="combinations_by_id"),
    path("__reload__/", include("django_browser_reload.urls")),
]
