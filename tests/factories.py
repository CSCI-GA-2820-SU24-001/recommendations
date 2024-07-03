"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyChoice
from service.models import Recommendation


class RecommendationFactory(factory.Factory):
    """Creates fake recommendations"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendation

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    product_id = factory.Faker("random_int", min=1, max=1000)
    recommended_product_id = factory.Faker("random_int", min=1, max=1000)
    recommendation_type = FuzzyChoice(["cross-sell", "up-sell", "accessory"])
