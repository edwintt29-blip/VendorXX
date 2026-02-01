# config.py - Central configuration for the procurement system

from dataclasses import dataclass
from typing import Dict

# =======================
# Scoring Weights
# =======================
SCORE_WEIGHTS = {
    "price": 0.50,      # 50% weight for price
    "delivery": 0.30,   # 30% weight for delivery speed
    "reliability": 0.20 # 20% weight for reliability
}

# Normalization bounds for scoring (in INR)
MAX_PRICE = 830000  # ~$10,000 USD
MAX_DELIVERY = 14  # days

# =======================
# Retry Configuration
# =======================
RETRY_CONFIG = {
    "max_attempts": 3,
    "base_delay": 0.5,      # seconds
    "max_delay": 5.0,       # seconds
    "exponential_base": 2,  # delay = base_delay * (exponential_base ^ attempt)
}

# =======================
# Vendor Configuration
# =======================
VENDOR_TIMEOUT = 10.0  # seconds - max wait for any vendor API

# =======================
# Database Configuration  
# =======================
DATABASE_PATH = "database.db"

# =======================
# Default Constraints (in INR)
# =======================
DEFAULT_BUDGET = 500000  # ~$6,000 USD
DEFAULT_DEADLINE = 6  # days


@dataclass
class Supplier:
    """Structured supplier data model"""
    name: str
    price: float
    delivery: int
    reliability: float
    score: float = 0.0
    negotiated_price: float = None
    
    def __post_init__(self):
        if self.negotiated_price is None:
            self.negotiated_price = self.price
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "price": self.price,
            "delivery": self.delivery,
            "reliability": self.reliability,
            "score": self.score,
            "negotiated_price": self.negotiated_price
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Supplier":
        return cls(
            name=data["name"],
            price=data["price"],
            delivery=data["delivery"],
            reliability=data["reliability"],
            score=data.get("score", 0.0),
            negotiated_price=data.get("negotiated_price")
        )
