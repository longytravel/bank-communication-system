"""
Communication Processing Module
Handles customer communication plans and cost configuration.
"""

from .cost_configuration import CostConfigurationManager, CommunicationCosts
from .customer_plans_ui import render_customer_communication_plans_page

def get_customer_plans_ui_renderer():
    """Get the customer plans UI renderer function."""
    return render_customer_communication_plans_page

__all__ = [
    'CostConfigurationManager',
    'CommunicationCosts',
    'render_customer_communication_plans_page',
    'get_customer_plans_ui_renderer'
]