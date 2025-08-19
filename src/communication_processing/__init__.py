"""
Communication Processing Module
Handles cost analysis, communication optimization, and batch processing.
"""

from .cost_configuration import CostConfigurationManager, CommunicationCosts
from .cost_integration import CostAnalyzer, render_cost_configuration_ui, render_cost_analyzer_ui
from .cost_controller import CommunicationCostController, integrate_cost_analysis_with_api_manager
from .batch_planner import BatchCommunicationPlanner

# Import batch_ui render function separately to avoid circular imports
__all__ = [
    'CostConfigurationManager',
    'CommunicationCosts', 
    'CostAnalyzer',
    'CommunicationCostController',
    'BatchCommunicationPlanner',
    'render_cost_configuration_ui',
    'render_cost_analyzer_ui',
    'integrate_cost_analysis_with_api_manager'
]

# Lazy import to avoid circular dependency
def get_batch_ui_renderer():
    """Get the batch UI renderer function when needed."""
    from .batch_ui import render_batch_communication_processing
    return render_batch_communication_processing