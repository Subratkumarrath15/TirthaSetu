"""
Analytics & Decision Insights Engine for YatraSafe Incident Command Platform.

Aggregates real-time crowd intelligence, IoT zone telemetry, predictive ML models,
and incident life-cycle records into actionable executive analytics and trend visualizations.
"""

import collections
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.incidents import incident_manager


class AnalyticsManager:
    """Thread-safe bounded in-memory store and aggregator for real-time intelligence analytics."""

    def __init__(self, maxlen: int = 200):
        self._lock = threading.Lock()
        self._snapshots = collections.deque(maxlen=maxlen)
        self._seed_baseline_data()

    def _seed_baseline_data(self):
        """Seed baseline telemetry across the 4 Gujarat temples to provide instant analytics on startup."""
        now = datetime.now()
        baselines = [
            ("Somnath", 22.45, "LOW", "STABLE", 22.0, 22.0, "Main Gate", 1018),
            ("Dwarka", 65.91, "MODERATE", "FALLING", 56.25, 60.0, "Darshan Queue", 2009),
            ("Ambaji", 84.42, "HIGH", "FALLING", 76.25, 80.0, "Darshan Queue", 4164),
            ("Pavagadh", 86.57, "CRITICAL", "RISING", 92.75, 95.0, "Darshan Queue", 2899),
        ]
        for temple, score, risk, trend, avg_d, max_d, peak_z, pred_v in baselines:
            self._snapshots.append({
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "temple": temple,
                "crowd_score": score,
                "risk_level": risk,
                "trend": trend,
                "live_average_density": avg_d,
                "max_zone_density": max_d,
                "highest_risk_zone": peak_z,
                "predicted_visitors": pred_v,
            })

    def record_snapshot(
        self,
        temple: str,
        crowd_score: float,
        risk_level: str,
        trend: str,
        live_average_density: float,
        max_zone_density: float,
        highest_risk_zone: str,
        predicted_visitors: int,
    ):
        """Record an atomic intelligence snapshot into the rolling history window."""
        with self._lock:
            snapshot = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temple": temple,
                "crowd_score": round(float(crowd_score), 2),
                "risk_level": risk_level,
                "trend": trend,
                "live_average_density": round(float(live_average_density), 2),
                "max_zone_density": round(float(max_zone_density), 2),
                "highest_risk_zone": highest_risk_zone or "General Area",
                "predicted_visitors": int(predicted_visitors),
            }
            self._snapshots.append(snapshot)

    def get_summary(self) -> Dict[str, Any]:
        """Compute executive KPI summary metrics across all recent intelligence snapshots."""
        with self._lock:
            snapshots = list(self._snapshots)

        if not snapshots:
            return {
                "average_crowd_score": 0.0,
                "highest_risk_temple": "None",
                "highest_risk_level": "LOW",
                "most_affected_zone": "None",
                "total_snapshots_recorded": 0,
                "incident_summary": {"total": 0, "active": 0, "resolved": 0, "critical": 0},
                "risk_level_distribution": {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0},
                "operational_insight": "No telemetry snapshots available.",
            }

        # 1. Average Crowd Score across rolling snapshots
        avg_score = round(sum(s["crowd_score"] for s in snapshots) / len(snapshots), 2)

        # 2. Determine Highest-Risk Shrine from the latest snapshot of each active Gujarat shrine
        # Risk Priority: CRITICAL (4) > HIGH (3) > MODERATE (2) > LOW (1), Tie-breaker: higher crowd_score
        risk_priority_map = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MODERATE": 2,
            "LOW": 1,
        }

        latest_by_temple: Dict[str, dict] = {}
        for s in reversed(snapshots):
            t_name = s.get("temple")
            if t_name and t_name not in latest_by_temple:
                latest_by_temple[t_name] = s

        if latest_by_temple:
            highest_risk_temple = max(
                latest_by_temple.keys(),
                key=lambda t: (
                    risk_priority_map.get(str(latest_by_temple[t].get("risk_level", "LOW")).upper(), 0),
                    float(latest_by_temple[t].get("crowd_score", 0.0))
                )
            )
            latest_snapshot_for_highest = latest_by_temple[highest_risk_temple]
            highest_risk_level = str(latest_snapshot_for_highest.get("risk_level", "LOW")).upper()
            most_affected_zone = latest_snapshot_for_highest.get("highest_risk_zone", "Darshan Queue")
        else:
            highest_risk_temple = "None"
            highest_risk_level = "LOW"
            most_affected_zone = "None"

        # 4. Risk Level Distribution
        risk_dist = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
        for s in snapshots:
            lvl = s.get("risk_level", "LOW")
            if lvl in risk_dist:
                risk_dist[lvl] += 1

        # 5. Incident Summary from IncidentManager
        active_incs = incident_manager.get_active_incidents()
        all_incs = incident_manager.get_incident_history(limit=200)

        total_inc = len(all_incs)
        active_inc = len(active_incs)
        resolved_inc = sum(1 for i in all_incs if i.get("status") == "RESOLVED")
        critical_inc = sum(1 for i in active_incs if i.get("risk_level") == "CRITICAL")

        # 6. Operational Insight Generation
        if critical_inc > 0 or highest_risk_level == "CRITICAL":
            insight = (
                f"CRITICAL crowd congestion concentrated at {highest_risk_temple} ({most_affected_zone}). "
                "Immediate gate expansions, vehicle parking diversions, and emergency medical dispatches active."
            )
        elif highest_risk_level == "HIGH":
            insight = (
                f"Elevated pilgrim saturation at {highest_risk_temple}. "
                f"Active queue bypass routing and barrier deployments recommended for {most_affected_zone}."
            )
        elif highest_risk_level == "MODERATE":
            insight = (
                f"Moderate weekend influx observed across {highest_risk_temple}. "
                "Continue standard queue monitoring and prepare overflow gates."
            )
        else:
            insight = "All monitored pilgrimage complexes operating smoothly within safe capacity thresholds."

        return {
            "average_crowd_score": avg_score,
            "highest_risk_temple": highest_risk_temple,
            "highest_risk_level": highest_risk_level,
            "most_affected_zone": most_affected_zone,
            "total_snapshots_recorded": len(snapshots),
            "incident_summary": {
                "total": total_inc,
                "active": active_inc,
                "resolved": resolved_inc,
                "critical": critical_inc,
            },
            "risk_level_distribution": risk_dist,
            "operational_insight": insight,
        }

    def get_trends(self, limit: int = 30) -> Dict[str, Any]:
        """Retrieve recent chronological snapshots for time-series trend charting."""
        with self._lock:
            recent = list(self._snapshots)[-limit:]

        return {
            "total_points": len(recent),
            "timestamps": [s["timestamp"] for s in recent],
            "series": recent,
        }

    def get_risk_distribution(self) -> Dict[str, Any]:
        """Calculate percentage and count breakdown of safety risk levels."""
        with self._lock:
            snapshots = list(self._snapshots)

        total = len(snapshots)
        counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
        for s in snapshots:
            lvl = s.get("risk_level", "LOW")
            if lvl in counts:
                counts[lvl] += 1

        percentages = {
            lvl: round((count / total) * 100, 1) if total > 0 else 0.0
            for lvl, count in counts.items()
        }

        return {
            "total_snapshots": total,
            "counts": counts,
            "percentages": percentages,
        }

    def get_temple_comparison(self) -> Dict[str, Any]:
        """Compare latest crowd status and metrics across the 4 Gujarat pilgrimage shrines."""
        temples = ["Somnath", "Dwarka", "Ambaji", "Pavagadh"]
        with self._lock:
            snapshots = list(self._snapshots)

        comparison = []
        for t in temples:
            # Find latest snapshot for this temple
            t_snaps = [s for s in snapshots if s["temple"].lower() == t.lower()]
            if t_snaps:
                latest = t_snaps[-1]
                avg_score = round(sum(s["crowd_score"] for s in t_snaps) / len(t_snaps), 2)
            else:
                latest = {
                    "crowd_score": 0.0,
                    "risk_level": "LOW",
                    "trend": "STABLE",
                    "live_average_density": 0.0,
                    "max_zone_density": 0.0,
                    "highest_risk_zone": "Main Gate",
                    "predicted_visitors": 0,
                }
                avg_score = 0.0

            # Count active incidents for this temple
            t_incidents = incident_manager.get_active_incidents(temple=t)

            comparison.append({
                "temple": t,
                "latest_crowd_score": latest["crowd_score"],
                "average_crowd_score": avg_score,
                "risk_level": latest["risk_level"],
                "trend": latest["trend"],
                "live_average_density": latest["live_average_density"],
                "max_zone_density": latest["max_zone_density"],
                "highest_risk_zone": latest["highest_risk_zone"],
                "predicted_visitors": latest["predicted_visitors"],
                "active_incidents": len(t_incidents),
            })

        # Sort by latest_crowd_score descending
        comparison.sort(key=lambda x: x["latest_crowd_score"], reverse=True)
        return {
            "total_temples": len(comparison),
            "comparison": comparison,
        }

    def get_incident_analytics(self) -> Dict[str, Any]:
        """Aggregate incident breakdowns by severity, temple, and resolution status."""
        active = incident_manager.get_active_incidents()
        history = incident_manager.get_incident_history(limit=200)

        by_temple: Dict[str, int] = {}
        by_zone: Dict[str, int] = {}
        by_risk: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}

        for inc in history:
            t = inc.get("temple", "General")
            z = inc.get("zone", "General Area")
            r = inc.get("risk_level", "HIGH")
            by_temple[t] = by_temple.get(t, 0) + 1
            by_zone[z] = by_zone.get(z, 0) + 1
            by_risk[r] = by_risk.get(r, 0) + 1

        return {
            "total_incidents": len(history),
            "active_incidents": len(active),
            "resolved_incidents": sum(1 for i in history if i.get("status") == "RESOLVED"),
            "breakdown_by_temple": by_temple,
            "breakdown_by_zone": by_zone,
            "breakdown_by_risk": by_risk,
        }


# Global Singleton Analytics Manager
analytics_manager = AnalyticsManager()
