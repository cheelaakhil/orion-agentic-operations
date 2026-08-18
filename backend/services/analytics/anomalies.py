"""
ORION Deterministic Anomaly Engine

Detects business metric anomalies through deterministic statistical comparison
between baseline and evaluation periods. Classifies severity using configurable
thresholds and produces structured AnomalyResult records without LLM dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.models.models import AnomalyRecordModel, SeverityLevel
from backend.services.analytics.customers import get_repeat_purchase_rate
from backend.services.analytics.inventory import get_stockout_rate
from backend.services.analytics.marketing import get_marketing_summary
from backend.services.analytics.orders import get_average_order_value, get_cancellation_rate, get_order_volume
from backend.services.analytics.revenue import get_total_revenue
from backend.services.analytics.support import get_average_resolution_time, get_sla_breach_rate


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyResult(BaseModel):
    """Structured representation of a detected statistical anomaly."""
    anomaly_id: str
    metric: str
    current_value: float
    baseline_value: float
    change_absolute: float
    change_percentage: float
    severity: AnomalySeverity
    affected_dimension: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    detected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AnomalyThresholds:
    """Configurable thresholds for classifying metric deviations."""
    # Revenue drop thresholds (negative percentage)
    revenue_low: float = -0.05       # -5%
    revenue_med: float = -0.12       # -12%
    revenue_high: float = -0.20      # -20%
    revenue_crit: float = -0.30      # -30%

    # Support SLA Breach Spike (absolute change in rate)
    sla_breach_low: float = 0.05     # +5%
    sla_breach_med: float = 0.12     # +12%
    sla_breach_high: float = 0.20    # +20%
    sla_breach_crit: float = 0.30    # +30%

    # Inventory Stockout Rate Spike (absolute change in rate)
    stockout_low: float = 0.05       # +5%
    stockout_med: float = 0.10       # +10%
    stockout_high: float = 0.20      # +20%
    stockout_crit: float = 0.30      # +30%

    # Repeat Purchase Rate Drop (negative percentage)
    repeat_rate_low: float = -0.05   # -5%
    repeat_rate_med: float = -0.15   # -15%
    repeat_rate_high: float = -0.25  # -25%
    repeat_rate_crit: float = -0.40  # -40%


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def classify_drop_severity(pct_change: float, t_low: float, t_med: float, t_high: float, t_crit: float) -> AnomalySeverity:
    """Classify metrics where a decrease represents deterioration (e.g. revenue, repeat purchase)."""
    if pct_change <= t_crit:
        return AnomalySeverity.CRITICAL
    elif pct_change <= t_high:
        return AnomalySeverity.HIGH
    elif pct_change <= t_med:
        return AnomalySeverity.MEDIUM
    elif pct_change <= t_low:
        return AnomalySeverity.LOW
    return AnomalySeverity.LOW


def classify_spike_severity(abs_change: float, t_low: float, t_med: float, t_high: float, t_crit: float) -> AnomalySeverity:
    """Classify metrics where an increase represents deterioration (e.g. SLA breach, stockouts)."""
    if abs_change >= t_crit:
        return AnomalySeverity.CRITICAL
    elif abs_change >= t_high:
        return AnomalySeverity.HIGH
    elif abs_change >= t_med:
        return AnomalySeverity.MEDIUM
    elif abs_change >= t_low:
        return AnomalySeverity.LOW
    return AnomalySeverity.LOW


# ---------------------------------------------------------------------------
# Core Anomaly Detection Engine
# ---------------------------------------------------------------------------

class DeterministicAnomalyEngine:
    """Evaluates business operations across dimensions against baseline windows."""

    def __init__(self, thresholds: AnomalyThresholds | None = None):
        self.thresholds = thresholds or AnomalyThresholds()

    def detect_all_anomalies(
        self,
        db: Session,
        baseline_start: datetime,
        baseline_end: datetime,
        evaluation_start: datetime,
        evaluation_end: datetime,
    ) -> list[AnomalyResult]:
        """
        Run statistical comparison across revenue, support, inventory, orders,
        and customer dimensions.
        """
        anomalies: list[AnomalyResult] = []

        # 1. Total Revenue Anomaly
        rev_base = get_total_revenue(db, baseline_start, baseline_end)
        rev_eval = get_total_revenue(db, evaluation_start, evaluation_end)

        # Normalize by day count if periods differ
        base_days = max(1, (baseline_end - baseline_start).days + 1)
        eval_days = max(1, (evaluation_end - evaluation_start).days + 1)
        daily_rev_base = rev_base / base_days
        daily_rev_eval = rev_eval / eval_days

        if daily_rev_base > 0:
            rev_change_abs = daily_rev_eval - daily_rev_base
            rev_change_pct = rev_change_abs / daily_rev_base

            if rev_change_pct <= self.thresholds.revenue_low:
                sev = classify_drop_severity(
                    rev_change_pct,
                    self.thresholds.revenue_low,
                    self.thresholds.revenue_med,
                    self.thresholds.revenue_high,
                    self.thresholds.revenue_crit,
                )
                anomalies.append(AnomalyResult(
                    anomaly_id="ANOM-REV-001",
                    metric="daily_revenue",
                    current_value=round(daily_rev_eval, 2),
                    baseline_value=round(daily_rev_base, 2),
                    change_absolute=round(rev_change_abs, 2),
                    change_percentage=round(rev_change_pct * 100, 2),
                    severity=sev,
                    affected_dimension="revenue",
                    evidence={
                        "baseline_period": f"{baseline_start.date()} to {baseline_end.date()}",
                        "evaluation_period": f"{evaluation_start.date()} to {evaluation_end.date()}",
                        "baseline_total": round(rev_base, 2),
                        "evaluation_total": round(rev_eval, 2),
                    },
                ))

        # 2. Support SLA Breach Rate Anomaly
        sla_base = get_sla_breach_rate(db, baseline_start, baseline_end)
        sla_eval = get_sla_breach_rate(db, evaluation_start, evaluation_end)
        sla_diff = sla_eval - sla_base

        if sla_diff >= self.thresholds.sla_breach_low:
            sev = classify_spike_severity(
                sla_diff,
                self.thresholds.sla_breach_low,
                self.thresholds.sla_breach_med,
                self.thresholds.sla_breach_high,
                self.thresholds.sla_breach_crit,
            )
            anomalies.append(AnomalyResult(
                anomaly_id="ANOM-SUP-001",
                metric="support_sla_breach_rate",
                current_value=round(sla_eval, 4),
                baseline_value=round(sla_base, 4),
                change_absolute=round(sla_diff, 4),
                change_percentage=round((sla_diff / max(0.001, sla_base)) * 100, 2),
                severity=sev,
                affected_dimension="support",
                evidence={
                    "baseline_sla_breach_rate": f"{sla_base * 100:.1f}%",
                    "evaluation_sla_breach_rate": f"{sla_eval * 100:.1f}%",
                    "avg_resolution_hours_baseline": get_average_resolution_time(db, baseline_start, baseline_end),
                    "avg_resolution_hours_evaluation": get_average_resolution_time(db, evaluation_start, evaluation_end),
                },
            ))

        # 3. Inventory Stockout Rate Anomaly
        stock_base = get_stockout_rate(db, baseline_start, baseline_end)
        stock_eval = get_stockout_rate(db, evaluation_start, evaluation_end)
        stock_diff = stock_eval - stock_base

        if stock_diff >= self.thresholds.stockout_low:
            sev = classify_spike_severity(
                stock_diff,
                self.thresholds.stockout_low,
                self.thresholds.stockout_med,
                self.thresholds.stockout_high,
                self.thresholds.stockout_crit,
            )
            anomalies.append(AnomalyResult(
                anomaly_id="ANOM-INV-001",
                metric="inventory_stockout_rate",
                current_value=round(stock_eval, 4),
                baseline_value=round(stock_base, 4),
                change_absolute=round(stock_diff, 4),
                change_percentage=round((stock_diff / max(0.001, stock_base)) * 100, 2),
                severity=sev,
                affected_dimension="inventory",
                evidence={
                    "baseline_stockout_rate": f"{stock_base * 100:.1f}%",
                    "evaluation_stockout_rate": f"{stock_eval * 100:.1f}%",
                },
            ))

        # 4. Repeat Purchase Rate Anomaly
        repeat_base = get_repeat_purchase_rate(db, baseline_start, baseline_end)
        repeat_eval = get_repeat_purchase_rate(db, evaluation_start, evaluation_end)

        if repeat_base > 0:
            repeat_change_abs = repeat_eval - repeat_base
            repeat_change_pct = repeat_change_abs / repeat_base

            if repeat_change_pct <= self.thresholds.repeat_rate_low:
                sev = classify_drop_severity(
                    repeat_change_pct,
                    self.thresholds.repeat_rate_low,
                    self.thresholds.repeat_rate_med,
                    self.thresholds.repeat_rate_high,
                    self.thresholds.repeat_rate_crit,
                )
                anomalies.append(AnomalyResult(
                    anomaly_id="ANOM-CUST-001",
                    metric="repeat_purchase_rate",
                    current_value=round(repeat_eval, 4),
                    baseline_value=round(repeat_base, 4),
                    change_absolute=round(repeat_change_abs, 4),
                    change_percentage=round(repeat_change_pct * 100, 2),
                    severity=sev,
                    affected_dimension="customers",
                    evidence={
                        "baseline_repeat_purchase_rate": f"{repeat_base * 100:.1f}%",
                        "evaluation_repeat_purchase_rate": f"{repeat_eval * 100:.1f}%",
                    },
                ))

        # 5. Order Cancellation Rate Anomaly
        canc_base = get_cancellation_rate(db, baseline_start, baseline_end)
        canc_eval = get_cancellation_rate(db, evaluation_start, evaluation_end)
        canc_diff = canc_eval - canc_base

        if canc_diff >= 0.02:  # +2% cancellation rate increase
            anomalies.append(AnomalyResult(
                anomaly_id="ANOM-ORD-001",
                metric="order_cancellation_rate",
                current_value=round(canc_eval, 4),
                baseline_value=round(canc_base, 4),
                change_absolute=round(canc_diff, 4),
                change_percentage=round((canc_diff / max(0.001, canc_base)) * 100, 2),
                severity=AnomalySeverity.MEDIUM if canc_diff < 0.05 else AnomalySeverity.HIGH,
                affected_dimension="orders",
                evidence={
                    "baseline_cancellation_rate": f"{canc_base * 100:.1f}%",
                    "evaluation_cancellation_rate": f"{canc_eval * 100:.1f}%",
                },
            ))

        return anomalies


# Default engine instance
anomaly_engine = DeterministicAnomalyEngine()
