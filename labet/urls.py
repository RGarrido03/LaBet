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
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from knox import views as knox_views
from rest_framework import permissions

from app.views import auth, bet, chart, game, user, tier

schema_view = get_schema_view(
    openapi.Info(
        title="LaBet API",
        default_version="v1",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"api/auth/login", auth.LoginView.as_view(), name="knox_login"),
    path(r"api/auth/logout", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(
        r"api/auth/logoutall",
        knox_views.LogoutAllView.as_view(),
        name="knox_logoutall",
    ),
    path("api/bet", bet.bet_games, name="bets"),
    path("api/bet/<int:id>", bet.new_bet, name="new_bet"),
    path("api/chart/history", chart.chart_history, name="chart_history"),
    path("api/chart/month", chart.chart_month, name="chart_month"),
    path("api/game", game.games, name="games"),
    path("api/game/<int:id>", game.game_by_id, name="game_by_id"),
    path("api/tier", tier.tier, name="tier"),
    path("api/tier/me", tier.tier_me, name="tier"),
    path("api/user", user.new_user, name="user"),
    path("api/user/me", user.user_me, name="user_me"),
    path("api/user/wallet", user.wallet, name="wallet"),
    path(
        "docs/swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "docs/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "docs/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
