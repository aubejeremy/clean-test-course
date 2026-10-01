from django.test import TestCase

# Create your tests here.
import pytest
from dataclasses import dataclass

# Assuming this represents an item in an order
@dataclass
class OrderItem:
    quantity: int

class Delivery:
    # Note: Added `self` if instantiated as a standard method,
    # or decorate with @staticmethod
    def calculate(self, order, distance):
        items = 0
        for item in order:
            items += item.quantity
        if items > 10 and distance > 5:
            return 7.50
        elif items > 5 and distance > 3:
            return 5
        else:
            return 2.5


@pytest.fixture
def delivery():
    return Delivery()


def make_order(*quantities):
    """Helper function to build an order list from item quantities."""
    return [OrderItem(quantity=q) for q in quantities]


# --- Tier 1: 7.50 (items > 10 and distance > 5) ---

@pytest.mark.parametrize("quantities,distance", [
    ([11], 5.1),           # Minimal boundary exceeding 10 items and 5 distance
    ([6, 5], 6),           # Multiple items summing to 11
    ([20], 10),            # Well inside the tier
])
def test_calculate_high_tier(delivery, quantities, distance):
    order = make_order(*quantities)
    assert delivery.calculate(order, distance) == 7.50


# --- Tier 2: 5.0 (items > 5 and distance > 3, but not falling into 7.50) ---

@pytest.mark.parametrize("quantities,distance", [
    ([6], 3.1),            # Minimal boundary exceeding 5 items and 3 distance
    ([10], 5),             # Exact thresholds of Tier 1 (10 items, 5 dist) -> falls to Tier 2
    ([15], 4),             # Items > 10, but distance <= 5 (falls out of Tier 1 into Tier 2)
    ([8], 10),             # Distance > 5, but items <= 10 (falls out of Tier 1 into Tier 2)
])
def test_calculate_mid_tier(delivery, quantities, distance):
    order = make_order(*quantities)
    assert delivery.calculate(order, distance) == 5


# --- Base Tier: 2.5 (All other conditions) ---

@pytest.mark.parametrize("quantities,distance", [
    ([], 10),              # Empty order (0 items)
    ([5], 3),              # Exact boundary of Tier 2 (5 items, 3 dist) -> falls to base
    ([5], 10),             # Items <= 5, high distance
    ([20], 3),             # Items > 10, but distance <= 3
    ([1, 2], 2),           # Low items and low distance
    ([0], 0),              # Zero quantity and zero distance
])
def test_calculate_base_tier(delivery, quantities, distance):
    order = make_order(*quantities)
    assert delivery.calculate(order, distance) == 2.5