from django.contrib.auth.models import AbstractUser
from django.db import models


class Tier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_bets = models.IntegerField(default=3)
    min_arbitrage = models.DecimalField(max_digits=10, decimal_places=2, default=0.95)
    max_wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    charts_included = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    birth_date = models.DateField(null=True)
    iban = models.CharField(max_length=34, null=True)

    def __str__(self):
        return self.username


class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)
    logo = models.URLField(null=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class BetHouse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.URLField(null=True)
    website = models.URLField()

    def __str__(self):
        return self.name


class GameOdd(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    away_odd = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.game} - {self.bet_house}"


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
    def odd(self):
        return 1 / self.home_odd + 1 / self.draw_odd + 1 / self.away_odd

    @property
    def profit(self):
        return (
            self.amount
            / (
                self.home_odd**-1
                + (self.draw_odd**-1 if self.draw_odd else 0)
                + self.away_odd**-1
            )
            - self.amount
        )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.game}"
