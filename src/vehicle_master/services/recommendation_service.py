# Full Path: src/vehicle_master/services/recommendation_service.py
# Relative Path: services/recommendation_service.py
# Module: vehicle_master
# Purpose: Applies BR-0003/BR-0008 (recommendation banding) to a computed price.
# Author: AI Agent (Claude, Sonnet 5)
# Related Documents: BRR-001 BR-0003/BR-0008, BUS-0005 (thresholds confirmed
#   90/75/60%), ISP-002 §4, EP-002
"""
``RecommendationService`` - a distinct service from ``ValuationService``,
matching SSD-001's own actor separation (Recommendation Service is a
separate participant in §3.4's sequence diagram). Pure calculation, no
repository dependency.
"""

from decimal import Decimal

#: BR-0003 thresholds, confirmed final via BUS-0005 - centrally defined
#: here (BR-0008: no module or screen may hardcode its own thresholds).
EXCELLENT_THRESHOLD = Decimal("0.90")
GOOD_THRESHOLD = Decimal("0.75")
AVERAGE_THRESHOLD = Decimal("0.60")

RECOMMENDATION_EXCELLENT = "EXCELLENT"
RECOMMENDATION_GOOD = "GOOD"
RECOMMENDATION_AVERAGE = "AVERAGE"
RECOMMENDATION_SCRAP = "SCRAP"


class RecommendationService:
    """Applies BR-0003/BR-0008 to a computed price."""

    def recommend(self, rounded_price: Decimal, minimum_selling_price: Decimal) -> str:
        """
        FR-002-008: score_percent = rounded_price / MSP, banded per
        BR-0003. Returns one of the four ``RECOMMENDATION_*`` constants.
        """
        if minimum_selling_price == 0:
            # MSP=0 edge case - genuinely undefined per FS-002/ISP-002
            # Open Questions; treated as SCRAP (0% of an undefined MSP)
            # rather than raising, to keep this method total. Flagged,
            # not silently assumed to be "correct" - see Open Questions.
            return RECOMMENDATION_SCRAP

        score_percent = rounded_price / minimum_selling_price

        if score_percent >= EXCELLENT_THRESHOLD:
            return RECOMMENDATION_EXCELLENT
        if score_percent >= GOOD_THRESHOLD:
            return RECOMMENDATION_GOOD
        if score_percent >= AVERAGE_THRESHOLD:
            return RECOMMENDATION_AVERAGE
        return RECOMMENDATION_SCRAP
