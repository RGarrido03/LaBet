from django_web_components import component


@component.register("tier_card")
class TierCard(component.Component):
    template_name = "components/tier-card.html"


@component.register("tier_feature")
class TierFeature(component.Component):
    template_name = "components/tier-feature.html"
