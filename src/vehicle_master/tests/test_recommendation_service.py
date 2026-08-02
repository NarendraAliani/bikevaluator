# Full Path: src/vehicle_master/tests/test_recommendation_service.py
# Relative Path: tests/test_recommendation_service.py
# Module: vehicle_master
# Purpose: Unit tests for RecommendationService - BR-0003/BR-0008 banding,
#   thresholds confirmed via BUS-0005.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0003/BR-0008, BUS-0005, ISP-002 §4, TEST-001
from decimal import Decimal

from django.test import SimpleTestCase

from vehicle_master.services.recommendation_service import (
    RECOMMENDATION_AVERAGE,
    RECOMMENDATION_EXCELLENT,
    RECOMMENDATION_GOOD,
    RECOMMENDATION_SCRAP,
    RecommendationService,
)


class RecommendationServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = RecommendationService()

    def test_br_0003_excellent_at_or_above_90_percent(self):
        self.assertEqual(
            self.service.recommend(Decimal("90"), Decimal("100")),
            RECOMMENDATION_EXCELLENT,
        )
        self.assertEqual(
            self.service.recommend(Decimal("100"), Decimal("100")),
            RECOMMENDATION_EXCELLENT,
        )

    def test_br_0003_good_between_75_and_89_percent(self):
        self.assertEqual(
            self.service.recommend(Decimal("75"), Decimal("100")), RECOMMENDATION_GOOD
        )
        self.assertEqual(
            self.service.recommend(Decimal("89"), Decimal("100")), RECOMMENDATION_GOOD
        )

    def test_br_0003_average_between_60_and_74_percent(self):
        self.assertEqual(
            self.service.recommend(Decimal("60"), Decimal("100")),
            RECOMMENDATION_AVERAGE,
        )
        self.assertEqual(
            self.service.recommend(Decimal("74"), Decimal("100")),
            RECOMMENDATION_AVERAGE,
        )

    def test_br_0003_scrap_below_60_percent(self):
        self.assertEqual(
            self.service.recommend(Decimal("59"), Decimal("100")), RECOMMENDATION_SCRAP
        )
        self.assertEqual(
            self.service.recommend(Decimal("0"), Decimal("100")), RECOMMENDATION_SCRAP
        )

    def test_boundary_just_below_each_threshold(self):
        """89.99% -> Good (not Excellent); 74.99% -> Average (not Good); 59.99% -> Scrap (not Average)."""
        self.assertEqual(
            self.service.recommend(Decimal("89.99"), Decimal("100")),
            RECOMMENDATION_GOOD,
        )
        self.assertEqual(
            self.service.recommend(Decimal("74.99"), Decimal("100")),
            RECOMMENDATION_AVERAGE,
        )
        self.assertEqual(
            self.service.recommend(Decimal("59.99"), Decimal("100")),
            RECOMMENDATION_SCRAP,
        )

    def test_msp_zero_edge_case_returns_scrap_not_error(self):
        """Genuinely undefined per FS-002/ISP-002 Open Questions - treated as SCRAP, not raised, flagged in code."""
        self.assertEqual(
            self.service.recommend(Decimal("0"), Decimal("0")), RECOMMENDATION_SCRAP
        )
