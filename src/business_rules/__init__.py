"""
Business Rules Module
Modular rule system for customer communication strategies.
"""

from .engine import BusinessRulesEngine
from .rules import *
from .customer_rules import CustomerCategoryRules
from .communication_rules import CommunicationRules

__all__ = [
    'BusinessRulesEngine',
    'CustomerCategoryRules', 
    'CommunicationRules'
] 
