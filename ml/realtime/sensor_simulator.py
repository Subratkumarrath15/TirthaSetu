"""
Real-Time IoT Sensor Simulator for YatraSafe AI Module.

Simulates stateful telemetry feeds for 4 pilgrimage temples across 4 distinct zones:
- Main Gate
- Darshan Queue
- Temple Entrance
- Parking

Generates inflow/outflow delta, calculates real-time accumulation, crowd density,
parking occupancy, and safety risk levels, saving the latest snapshot to
realtime/latest_sensor_data.json every 3 seconds.
"""

import argparse
import json
import os
import random
import signal
import sys
import time
from datetime import datetime

# Temple zone capacity configurations for the 4 Gujarat pilgrimage sites
ZONE_CONFIGS = {
    "Somnath": {
        "Main Gate": {"capacity": 3500, "inflow_mean": 12, "inflow_std": 3, "initial": 1250},
        "Darshan Queue": {"capacity": 10000, "inflow_mean": 16, "inflow_std": 4, "initial": 3900},
        "Temple Entrance": {"capacity": 3000, "inflow_mean": 10, "inflow_std": 3, "initial": 1150},
        "Parking": {"capacity": 2500, "inflow_mean": 6, "inflow_std": 2, "initial": 980},
    },
    "Dwarka": {
        "Main Gate": {"capacity": 3000, "inflow_mean": 11, "inflow_std": 3, "initial": 1100},
        "Darshan Queue": {"capacity": 9000, "inflow_mean": 15, "inflow_std": 4, "initial": 3400},
        "Temple Entrance": {"capacity": 2500, "inflow_mean": 9, "inflow_std": 2, "initial": 950},
        "Parking": {"capacity": 2000, "inflow_mean": 5, "inflow_std": 2, "initial": 750},
    },
    "Ambaji": {
        "Main Gate": {"capacity": 4500, "inflow_mean": 15, "inflow_std": 4, "initial": 1650},
        "Darshan Queue": {"capacity": 14000, "inflow_mean": 20, "inflow_std": 5, "initial": 5800},
        "Temple Entrance": {"capacity": 4000, "inflow_mean": 13, "inflow_std": 3, "initial": 1500},
        "Parking": {"capacity": 3000, "inflow_mean": 8, "inflow_std": 2, "initial": 1200},
    },
    "Pavagadh": {
        "Main Gate": {"capacity": 2000, "inflow_mean": 8, "inflow_std": 2, "initial": 620},
        "Darshan Queue": {"capacity": 6000, "inflow_mean": 10, "inflow_std": 3, "initial": 2100},
        "Temple Entrance": {"capacity": 1800, "inflow_mean": 7, "inflow_std": 2, "initial": 550},
        "Parking": {"capacity": 1200, "inflow_mean": 4, "inflow_std": 1, "initial": 420},
    },
}

SUPPORTED_TEMPLES = list(ZONE_CONFIGS.keys())
SUPPORTED_ZONES = ["Main Gate", "Darshan Queue", "Temple Entrance", "Parking"]


def calculate_risk_level(density_pct: float) -> str:
    """Classify crowd density percentage into standardized risk tiers."""
    if density_pct < 40.0:
        return "LOW"
    elif density_pct < 70.0:
        return "MODERATE"
    elif density_pct < 85.0:
        return "HIGH"
    else:
        return "CRITICAL"


class TempleSensorSimulator:
    """Stateful real-time crowd and IoT telemetry engine."""

    def __init__(self, output_file: str = None):
        if output_file is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_file = os.path.join(script_dir, "latest_sensor_data.json")
        else:
            self.output_file = output_file

        # Initialize internal persistent state per temple and zone
        self.state = {}
        for temple, zones in ZONE_CONFIGS.items():
            self.state[temple] = {}
            for zone, cfg in zones.items():
                self.state[temple][zone] = {
                    "current_people": cfg["initial"],
                    "capacity": cfg["capacity"],
                }

        self.cycle_count = 0
        self.running = True

    def step(self) -> dict:
        """Execute one simulation cycle and return stateful sensor snapshot."""
        self.cycle_count += 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        records = []

        for temple, zones in ZONE_CONFIGS.items():
            for zone, cfg in zones.items():
                prev_people = self.state[temple][zone]["current_people"]
                capacity = cfg["capacity"]
                inflow_mean = cfg["inflow_mean"]
                inflow_std = cfg["inflow_std"]

                # Generate realistic inflow & outflow with controlled stochastic variance
                entering = max(0, int(round(random.gauss(inflow_mean, inflow_std))))
                # Outflow fluctuates naturally with slight bias towards equilibrium
                outflow_rate = random.uniform(0.85, 1.15)
                exiting = max(0, int(round(entering * outflow_rate + random.randint(-2, 2))))

                # Calculate new stateful current_people
                new_people = max(0, prev_people + entering - exiting)
                self.state[temple][zone]["current_people"] = new_people

                # Calculate density percentage
                raw_density = (new_people / capacity) * 100.0
                crowd_density = round(min(100.0, max(0.0, raw_density)), 2)
                risk_level = calculate_risk_level(crowd_density)

                # Parking occupancy (only populated for Parking zone)
                if zone == "Parking":
                    parking_occupancy = crowd_density
                else:
                    parking_occupancy = None

                record = {
                    "temple": temple,
                    "zone": zone,
                    "people_entering": entering,
                    "people_exiting": exiting,
                    "current_people": new_people,
                    "crowd_density": crowd_density,
                    "parking_occupancy": parking_occupancy,
                    "risk_level": risk_level,
                    "timestamp": now_str,
                }
                records.append(record)

        snapshot = {
            "cycle": self.cycle_count,
            "timestamp": now_str,
            "total_records": len(records),
            "sensors": records,
        }

        # Save latest state to JSON
        self.save_state(snapshot)
        return snapshot

    def save_state(self, snapshot: dict):
        """Atomically persist snapshot to latest_sensor_data.json."""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4)

    def print_cycle_summary(self, snapshot: dict):
        """Format and print real-time telemetry to console."""
        cycle = snapshot["cycle"]
        ts = snapshot["timestamp"]
        print(f"\n[{ts}] === SIMULATION CYCLE #{cycle:03d} ===")
        print(f"{'Temple':<14} | {'Zone':<16} | {'In/Out':<10} | {'Current People':<14} | {'Density':<8} | {'Risk Level'}")
        print("-" * 85)

        for rec in snapshot["sensors"]:
            in_out = f"+{rec['people_entering']}/-{rec['people_exiting']}"
            cur_pop = f"{rec['current_people']:,}"
            density = f"{rec['crowd_density']:.1f}%"
            risk = rec["risk_level"]
            print(f"{rec['temple']:<14} | {rec['zone']:<16} | {in_out:<10} | {cur_pop:<14} | {density:<8} | {risk}")

    def run(self, update_interval: int = 3, max_cycles: int = None):
        """Main simulation loop."""
        print("=" * 85)
        print(">> YATRASAFE REAL-TIME IOT SENSOR SIMULATOR ACTIVE")
        print(f">> Update Interval: {update_interval}s | Press Ctrl+C to stop cleanly")
        print(f">> State persistence: {self.output_file}")
        print("=" * 85)

        def sigint_handler(sig, frame):
            print("\n\n[INFO] Termination signal received. Saving final state and exiting gracefully...")
            self.running = False

        signal.signal(signal.SIGINT, sigint_handler)

        try:
            while self.running:
                snapshot = self.step()
                self.print_cycle_summary(snapshot)

                if max_cycles is not None and self.cycle_count >= max_cycles:
                    print(f"\n[INFO] Reached requested {max_cycles} test cycles. Simulation complete.")
                    break

                # Sleep in small increments for responsive Ctrl+C handling
                for _ in range(int(update_interval * 10)):
                    if not self.running:
                        break
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt caught.")
        finally:
            print(f"[SUCCESS] Final simulation state saved to {self.output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YatraSafe IoT Sensor Simulator")
    parser.add_argument("--interval", type=int, default=3, help="Update interval in seconds (default: 3)")
    parser.add_argument("--cycles", type=int, default=None, help="Number of cycles to run (default: infinite)")
    args = parser.parse_args()

    simulator = TempleSensorSimulator()
    simulator.run(update_interval=args.interval, max_cycles=args.cycles)
