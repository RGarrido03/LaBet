from django.db import models
from django.contrib.auth.models import AbstractUser


class Tier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()


class User(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    birth_date = models.DateField(null=True)
    iban = models.CharField(max_length=34, null=True)


class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)
    logo = models.ImageField(upload_to="static/logos")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_team"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_team"
    )
    date = models.DateTimeField()

    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)


class BetHouse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="static/logos")
    website = models.URLField()


class GameOdd(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    away_odd = models.DecimalField(max_digits=10, decimal_places=2)


class Bet(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    home_bet_house = models.ForeignKey(
        BetHouse, on_delete=models.CASCADE, related_name="home_bet_house"
    )
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)

    draw_bet_house = models.ForeignKey(
        BetHouse, on_delete=models.CASCADE, related_name="draw_bet_house", null=True
    )
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    away_bet_house = models.ForeignKey(
        BetHouse, on_delete=models.CASCADE, related_name="away_bet_house"
    )
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
