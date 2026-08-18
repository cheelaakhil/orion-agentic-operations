"""
DataAnalysisAgent Interface

Retrieves and structures business data across all investigation dimensions.
Performs deterministic SQL queries and statistical calculations.

CRITICAL: This agent performs NO LLM-based numerical computation.
All numbers come from SQL queries and Python statistics libraries.
"""

from typing import Any, Type

from pydantic import BaseModel, Field

from .base import AnomalyRecord, BaseAgent, TimeRange


# ---------------------------------------------------------------------------
# Output Sub-Schemas
# ---------------------------------------------------------------------------

class MetricSummary(BaseModel):
    """Summary statistics for a single metric."""
    metric_name: str
    current_value: float
    previous_value: float
    change_pct: float
    period: TimeRange
    unit: str = ""


class TrendAnalysis(BaseModel):
    """Trend analysis for a metric over time."""
    metric_name: str
    direction: str = Field(..., description="increasing | decreasing | stable")
    slope: float
    r_squared: float
    change_point_date: str | None = None
    data_points: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Time series data: [{date, value}, ...]",
    )


class StatisticalTest(BaseModel):
    """Result of a statistical significance test."""
    test_name: str
    metric: str
    test_statistic: float
    p_value: float
    significant: bool
    interpretation: str


class NotableChange(BaseModel):
    """A notable change detected in the data."""
    dimension: str
    metric: str
    description: str
    magnitude: float
    onset_date: str | None = None


class Correlation(BaseModel):
    """Correlation between two metrics."""
    metric_a: str
    metric_b: str
    coefficient: float
    p_value: float
    method: str = "pearson"
    interpretation: str = ""


class DataQualityReport(BaseModel):
    """Report on data completeness and quality."""
    total_queries: int
    successful_queries: int
    missing_data_flags: list[str] = Field(default_factory=list)
    data_coverage_pct: float


class DimensionAnalysis(BaseModel):
    """Analysis results for a single dimension."""
    dimension: str
    metric_summaries: list[MetricSummary]
    trends: list[TrendAnalysis]
    statistical_tests: list[StatisticalTest]
    notable_changes: list[NotableChange]


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class DataAnalysisInput(BaseModel):
    """Input to the DataAnalysisAgent."""
    investigation_id: str
    anomaly: AnomalyRecord
    dimensions: list[str]
    time_range: TimeRange


class DataAnalysisOutput(BaseModel):
    """Output from the DataAnalysisAgent."""
    investigation_id: str
    dimension_analyses: dict[str, DimensionAnalysis]
    cross_dimension_correlations: list[Correlation]
    data_quality: DataQualityReport


# ---------------------------------------------------------------------------
# Agent Interface
# ---------------------------------------------------------------------------

class DataAnalysisAgent(BaseAgent):
    """
    Retrieves and structures business data for investigation.

    This agent runs deterministic SQL queries and statistical
    calculations. It does NOT use an LLM for any numerical work.
    """

    @property
    def name(self) -> str:
        return "data_analysis_agent"

    @property
    def description(self) -> str:
        return (
            "Retrieves business data across all investigation dimensions "
            "and performs deterministic statistical analysis."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        return DataAnalysisInput

    @property
    def output_schema(self) -> Type[BaseModel]:
        return DataAnalysisOutput

    @property
    def tools(self) -> list[str]:
        return [
            "query_revenue_metrics",
            "query_customer_metrics",
            "query_support_metrics",
            "query_inventory_metrics",
            "query_marketing_metrics",
            "compute_statistical_tests",
        ]

    async def execute(self, input_data: DataAnalysisInput) -> DataAnalysisOutput:
        raise NotImplementedError("Implement in concrete provider class")

    async def validate_output(self, output: DataAnalysisOutput) -> bool:
        if not output.dimension_analyses:
            return False
        if output.data_quality.data_coverage_pct < 50.0:
            return False
        return True
