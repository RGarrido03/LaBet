from django_web_components import component


@component.register("tier_card")
class TierCard(component.Component):
    template_name = "components/tier-card.html"


@component.register("tier_feature")
class TierFeature(component.Component):
    template_name = "components/tier-feature.html"


@component.register("landing_card")
class LandingCard(component.Component):
    template_name = "components/landing-card.html"


@component.register("game_card")
class GameCard(component.Component):
    template_name = "components/game-card.html"


@component.register("house_card")
class TierCard(component.Component):
    template_name = "components/house-card.html"
