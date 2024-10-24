from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms.models import model_to_dict


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

    def to_json(self):
        return model_to_dict(self)


class User(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    birth_date = models.DateField(null=True)
    iban = models.CharField(max_length=34, null=True)

    def __str__(self):
        return self.username

    def to_json(self):
        user_dict = model_to_dict(self)
        user_dict["tier"] = self.tier.to_json() if self.tier else None
        return user_dict


class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def to_json(self):
        return model_to_dict(self)


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=3)
    logo = models.URLField(null=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def to_json(self):
        team_dict = model_to_dict(self)
        team_dict["sport"] = self.sport.to_json()
        return team_dict


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

    def to_json(self):
        game_dict = model_to_dict(self)
        game_dict["home_team"] = self.home_team.to_json()
        game_dict["away_team"] = self.away_team.to_json()
        return game_dict


class BetHouse(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.URLField(null=True)
    website = models.URLField()

    def __str__(self):
        return self.name

    def to_json(self):
        return model_to_dict(self)


class GameOdd(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bet_house = models.ForeignKey(BetHouse, on_delete=models.CASCADE)
    home_odd = models.DecimalField(max_digits=10, decimal_places=2)
    draw_odd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    away_odd = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.game} - {self.bet_house}"

    def to_json(self):
        odd_dict = model_to_dict(self)
        odd_dict["game"] = self.game.to_json()  # Incluindo o jogo
        odd_dict["bet_house"] = self.bet_house.to_json()  # Incluindo a casa de apostas
        return odd_dict


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

    def __str__(self):
        return f"{self.user} - {self.game}"

    def to_json(self):
        bet_dict = model_to_dict(self)
        bet_dict["user"] = self.user.to_json()
        bet_dict["game"] = self.game.to_json()
        bet_dict["home_bet_house"] = self.home_bet_house.to_json()
        bet_dict["draw_bet_house"] = (
            self.draw_bet_house.to_json() if self.draw_bet_house else None
        )
        bet_dict["away_bet_house"] = self.away_bet_house.to_json()
        return bet_dict
