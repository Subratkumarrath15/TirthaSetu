"""
Incident Management Module for YatraSafe AI + Real-Time Incident Command Center.

Tracks, synchronizes, acknowledges, and resolves real-time crowd safety incidents
triggered by the Crowd Intelligence Engine and IoT sensor alerts.
"""

import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional


class IncidentManager:
    """Thread-safe in-memory Incident Store and Lifecycle Manager."""

    def __init__(self):
        self._lock = threading.Lock()
        self._incidents: Dict[str, dict] = {}
        self._incident_counter = 1

    def _generate_id(self, temple: str) -> str:
        code = temple[:3].upper() if temple else "YTR"
        now_str = datetime.now().strftime("%Y%m%d")
        inc_id = f"INC-{code}-{now_str}-{self._incident_counter:03d}"
        self._incident_counter += 1
        return inc_id

    def sync_from_alerts(self, alerts: List[dict], temple: str) -> List[dict]:
        """
        Synchronize incidents from Crowd Intelligence Engine zone alerts.
        Prevents duplicate active incidents for the same (temple, zone).
        """
        with self._lock:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            synced = []

            for a in alerts:
                zone = a.get("zone", "General Area")
                risk_level = a.get("risk_level", "HIGH")
                density = float(a.get("zone_density", 0.0))
                message = a.get(
                    "recommended_immediate_action",
                    f"Elevated crowd saturation detected in {zone} ({density}%). Immediate queue relief required.",
                )

                # Check for existing ACTIVE or ACKNOWLEDGED incident for this (temple, zone)
                existing = None
                for inc in self._incidents.values():
                    if (
                        inc["temple"] == temple
                        and inc["zone"] == zone
                        and inc["status"] in ("ACTIVE", "ACKNOWLEDGED")
                    ):
                        existing = inc
                        break

                if existing:
                    # Update live density and message
                    existing["density"] = density
                    existing["risk_level"] = risk_level
                    existing["message"] = message
                    existing["updated_at"] = now_str
                    synced.append(existing)
                else:
                    # Create new incident
                    inc_id = self._generate_id(temple)
                    new_inc = {
                        "incident_id": inc_id,
                        "temple": temple,
                        "zone": zone,
                        "risk_level": risk_level,
                        "density": density,
                        "message": message,
                        "status": "ACTIVE",
                        "created_at": now_str,
                        "updated_at": now_str,
                        "acknowledged_at": None,
                        "resolved_at": None,
                    }
                    self._incidents[inc_id] = new_inc
                    synced.append(new_inc)

            return synced

    def get_active_incidents(self, temple: Optional[str] = None) -> List[dict]:
        """Retrieve all active or acknowledged incidents, optionally filtered by temple."""
        with self._lock:
            active = [
                inc for inc in self._incidents.values()
                if inc["status"] in ("ACTIVE", "ACKNOWLEDGED")
            ]
            if temple:
                active = [inc for inc in active if inc["temple"].lower() == temple.lower()]
            # Sort by priority (CRITICAL first, then highest density)
            active.sort(
                key=lambda x: (1 if x["risk_level"] == "CRITICAL" else 0, x["density"]),
                reverse=True,
            )
            return list(active)

    def get_incident_history(self, limit: int = 50) -> List[dict]:
        """Retrieve historical incidents (resolved and active) sorted by created_at desc."""
        with self._lock:
            all_inc = list(self._incidents.values())
            all_inc.sort(key=lambda x: x["created_at"], reverse=True)
            return all_inc[:limit]

    def acknowledge_incident(self, incident_id: str) -> Optional[dict]:
        """Mark an incident as ACKNOWLEDGED by a government operator."""
        with self._lock:
            inc = self._incidents.get(incident_id)
            if not inc:
                return None
            if inc["status"] == "ACTIVE":
                inc["status"] = "ACKNOWLEDGED"
                inc["acknowledged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return dict(inc)

    def resolve_incident(self, incident_id: str) -> Optional[dict]:
        """Mark an incident as RESOLVED."""
        with self._lock:
            inc = self._incidents.get(incident_id)
            if not inc:
                return None
            inc["status"] = "RESOLVED"
            inc["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return dict(inc)

    def seed_demo_incidents(self, scenario_name: str, alerts: List[dict], temple: str):
        """Seed controlled incidents for demo presentation."""
        self.sync_from_alerts(alerts, temple)

    def clear_all(self):
        """Clear all incidents (for testing)."""
        with self._lock:
            self._incidents.clear()
            self._incident_counter = 1


# Global Singleton Instance
incident_manager = IncidentManager()
