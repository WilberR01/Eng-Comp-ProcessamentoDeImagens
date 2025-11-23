"""Model classes used across the project (report items, consolidated report, etc.).
"""

from .report import ResultItem, ConsolidatedReport
from .analysis import AnalysisResult

__all__ = ["ResultItem", "ConsolidatedReport", "AnalysisResult"]
