from django.db import models
from django.contrib.auth.models import User as BaseUser


class Tier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()


class User(BaseUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    birth_date = models.DateField()
    iban = models.CharField(max_length=34)


class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)
    logo = models.ImageField(upload_to="static/logos")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE)
    date = models.DateTimeField()

    home_score = models.IntegerField()
    away_score = models.IntegerField()


class BetHouse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="static/logos")
    website = models.URLField()


# GameOdds
class Game_BetHouse(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    away_odd = models.DecimalField(max_digits=10, decimal_places=2)


class Bet(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    home_bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)

    draw_bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE, null=True)
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    away_bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    away_odd = models.DecimalField(max_digits=10, decimal_places=2)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def profit(self):
        return self.amount / (
            self.home_odd**-1
            + (self.draw_odd**-1 if self.draw_odd else 0)
            + self.away_odd**-1
        )

    created_at = models.DateTimeField(auto_now_add=True)
