from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models import User, Tier, Bet, BetHouse, Game, GameOdd, Sport, Team

admin.site.register(User, UserAdmin)
admin.site.register(Tier)
admin.site.register(Bet)
admin.site.register(BetHouse)
admin.site.register(Game)
admin.site.register(GameOdd)
admin.site.register(Sport)
admin.site.register(Team)
