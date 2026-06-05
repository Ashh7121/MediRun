"""
Delivery assignment service.
Can be run standalone:  python services/assign_driver.py
Or imported by Flask:   from assign_driver import AssignDeliveriesService

geopy is used when available; a built-in Haversine fallback is used otherwise
so the app works out of the box without extra system packages.
"""

import os
import sys
import math
from collections import defaultdict

# Make sure test_dummy_data is importable whether this file is run directly
# or imported by Flask (which adds services/ to sys.path via app.py)
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from test_dummy_data import DELIVERIES, DRIVERS, WAREHOUSE

CLUSTER_DISTANCE = 5   # km — deliveries within this radius form a cluster
VAN_THRESHOLD    = 3   # max extra deliveries added to a seed cluster


# ── Distance calculation ───────────────────────────────────────────────────────

def _haversine(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in km between two GPS points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


try:
    from geopy.distance import geodesic as _geodesic

    def _distance_km(lat1, lon1, lat2, lon2):
        return _geodesic((lat1, lon1), (lat2, lon2)).kilometers

except ImportError:
    # geopy not installed — use the pure-Python Haversine formula
    def _distance_km(lat1, lon1, lat2, lon2):
        return _haversine(lat1, lon1, lat2, lon2)


# ── Mixins ─────────────────────────────────────────────────────────────────────

class DistanceCalculatorMixin:
    """Geodesic distance helpers used by the assignment algorithm."""

    def calculate_distance(self, loc1, loc2):
        return _distance_km(
            loc1['location']['lat'], loc1['location']['lng'],
            loc2['location']['lat'], loc2['location']['lng'],
        )

    def calculate_distance_from_warehouse(self, loc, warehouse):
        return _distance_km(
            loc['location']['lat'], loc['location']['lng'],
            warehouse['lat'], warehouse['lng'],
        )

    def calculate_distances_from_warehouse(self, deliveries, warehouse):
        return [
            _distance_km(
                d['location']['lat'], d['location']['lng'],
                warehouse['lat'], warehouse['lng'],
            )
            for d in deliveries
        ]

    def build_clusters(self, deliveries):
        """
        Greedy geographic clustering.
        Each cluster grows from a seed delivery and absorbs nearby deliveries
        until no more fit within CLUSTER_DISTANCE or VAN_THRESHOLD is reached.
        """
        unvisited = deliveries.copy()
        clusters  = []

        while unvisited:
            seed    = unvisited.pop()
            cluster = [seed]
            stack   = [seed]

            while stack:
                current = stack.pop()
                for delivery in list(unvisited):
                    if (
                        self.calculate_distance(current, delivery) < CLUSTER_DISTANCE
                        and len(cluster) <= VAN_THRESHOLD
                    ):
                        cluster.append(delivery)
                        stack.append(delivery)
                        unvisited.remove(delivery)

            clusters.append(cluster)
        return clusters

    def calculate_max_distance(self, cluster, warehouse):
        return max(self.calculate_distances_from_warehouse(cluster, warehouse))

    def calculate_average_distance(self, cluster, warehouse):
        dists = self.calculate_distances_from_warehouse(cluster, warehouse)
        return sum(dists) / len(dists)

    def score_cluster(self, cluster):
        """Priority score: critical deliveries dominate the sort."""
        weights = {'critical': 100, 'high': 10, 'normal': 1}
        return sum(weights.get(d['priority'], 0) for d in cluster)


class DeliveryFilterMixin:
    """Helpers to split the delivery list by temperature and priority."""

    def filter_temp_sensitive(self, deliveries):
        return [d for d in deliveries if d['temperature_sensitive']]

    def filter_regular(self, deliveries):
        return [d for d in deliveries if not d['temperature_sensitive']]

    def filter_by_priority(self, deliveries):
        non_temp = self.filter_regular(deliveries)
        return (
            [d for d in non_temp if d['priority'] == 'critical'],
            [d for d in non_temp if d['priority'] == 'high'],
            [d for d in non_temp if d['priority'] == 'normal'],
        )


# ── Main service ───────────────────────────────────────────────────────────────

class AssignDeliveriesService(DeliveryFilterMixin, DistanceCalculatorMixin):
    """
    Naïve but justified delivery-assignment strategy:

    Step 1  Temperature-sensitive deliveries → refrigerated van driver.
    Step 2  Remaining deliveries are geo-clustered (Haversine / geopy).
    Step 3  Clusters classified as short-distance (urban, avg ≤ 8 km & max ≤ 15 km)
            or long-distance (peri-urban, exceeds those thresholds).
    Step 4  Clusters sorted by priority score (critical first).
    Step 5  Long-distance clusters → large-van drivers (round-robin).
            Short-distance clusters → small-van drivers (round-robin).

    Hard constraints enforced:
    - Temp-sensitive product → refrigerated vehicle only.
    - Cluster size capped at VAN_THRESHOLD to avoid overloading a single van.

    Soft optimisation:
    - Priority ordering within each distance group.
    - Geographic clustering minimises total travel distance.
    """

    def __init__(self, deliveries=None, drivers=None, warehouse=None):
        self.deliveries  = deliveries if deliveries is not None else DELIVERIES
        self.drivers     = drivers    if drivers    is not None else DRIVERS
        self.warehouse   = warehouse  if warehouse  is not None else WAREHOUSE
        self.assignments = self.assign_all()

    # ── Driver selection helpers ───────────────────────────────────────────────

    def get_refrigerated_driver(self):
        return next((d for d in self.drivers if d['van_type'] == 'refrigerated'), None)

    def get_large_van_drivers(self):
        return [d for d in self.drivers if d['van_type'] == 'big']

    def get_small_van_drivers(self):
        return [d for d in self.drivers if d['van_type'] == 'small']

    # ── Core algorithm ─────────────────────────────────────────────────────────

    def assign_all(self):
        """Orchestrate the full assignment and return {driver_id: [delivery_id]}."""
        assignments = defaultdict(list)

        # Step 1 — temperature-sensitive → refrigerated driver ─────────────────
        fridge_driver   = self.get_refrigerated_driver()
        temp_deliveries = self.filter_temp_sensitive(self.deliveries)

        if fridge_driver:
            for delivery in temp_deliveries:
                assignments[fridge_driver['id']].append(delivery['id'])
        else:
            # Fallback: no refrigerated driver → use large vans
            large = self.get_large_van_drivers()
            for i, delivery in enumerate(temp_deliveries):
                if large:
                    assignments[large[i % len(large)]['id']].append(delivery['id'])

        # Step 2 — cluster non-temp-sensitive deliveries ───────────────────────
        regular  = self.filter_regular(self.deliveries)
        clusters = self.build_clusters(regular)

        long_distance_clusters  = []
        short_distance_clusters = []

        for cluster in clusters:
            max_dist = self.calculate_max_distance(cluster, self.warehouse)
            avg_dist = self.calculate_average_distance(cluster, self.warehouse)
            if avg_dist <= 8 and max_dist <= 15:
                short_distance_clusters.append(cluster)
            else:
                long_distance_clusters.append(cluster)

        # Step 3 — sort by priority score (critical first) ─────────────────────
        long_distance_clusters.sort(key=lambda c: self.score_cluster(c), reverse=True)
        short_distance_clusters.sort(key=lambda c: self.score_cluster(c), reverse=True)

        # Step 4 — assign to drivers ───────────────────────────────────────────
        big_drivers   = self.get_large_van_drivers()
        small_drivers = self.get_small_van_drivers()

        for i, cluster in enumerate(long_distance_clusters):
            pool = big_drivers or small_drivers
            if pool:
                driver = pool[i % len(pool)]
                for delivery in cluster:
                    assignments[driver['id']].append(delivery['id'])

        for i, cluster in enumerate(short_distance_clusters):
            pool = small_drivers or big_drivers
            if pool:
                driver = pool[i % len(pool)]
                for delivery in cluster:
                    assignments[driver['id']].append(delivery['id'])

        return assignments

    def __repr__(self):
        lines = []
        driver_map = {d['id']: d['name'] for d in self.drivers}
        for driver_id, delivery_ids in self.assignments.items():
            name = driver_map.get(driver_id, f'Driver {driver_id}')
            lines.append(f"{name}: {len(delivery_ids)} deliveries → IDs {delivery_ids}")
        return '\n'.join(lines)


# ── Standalone smoke-test ──────────────────────────────────────────────────────
if __name__ == '__main__':
    service = AssignDeliveriesService()
    print(service)
    print(f"\nTotal assigned: {sum(len(v) for v in service.assignments.values())} / {len(DELIVERIES)}")
