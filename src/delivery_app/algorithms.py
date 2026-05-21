# Core optimization algorithms
from test_dummy_data import DELIVERIES
# TODO: Filter temperature-sensitive deliveries (must use refrigerated van)
def filter_temperature_sensitive(deliveries):
    filtered=[]
    for delivery in deliveries:
        if delivery['temperature_sensitive']:
            filtered.append(delivery)
    return filtered


# TODO: Sort deliveries by urgency (hospitals first, clinics second, pharmacies last)
def sort_by_urgency(deliveries):
    priorities={
        "hospital":1,
        "clinic":2,
        "pharmacy":3
    }
    return sorted(deliveries,key=lambda delivery:priorities.get(delivery["destination_type"],4))

# TODO: Assign deliveries to vehicle types based on distance
# Far deliveries (>X km) → big vans
# Near deliveries → small vans
def assign_to_vehicle_types(deliveries, distances_from_warehouse):
    pass


# TODO: Distribute deliveries among drivers (load balancing)
def distribute_to_drivers(deliveries_by_vehicle, available_drivers):
    pass


# TODO: Apply topological sort to enforce urgency constraints
# Returns ordering where urgent deliveries come before non-urgent
def topological_sort_by_urgency(deliveries_for_driver):
    pass


# TODO: Apply greedy sort within topological constraints
# Among all valid next deliveries (per topological order), pick closest to current location
def greedy_closest_next_stop(current_location, remaining_deliveries, distances):
    pass


# TODO: Main orchestration function
# Combines all steps: filter → assign vehicles → distribute → order → optimize
def optimize_daily_deliveries(all_deliveries, drivers, distances_from_warehouse):
    pass

# print(filter_temperature_sensitive(DELIVERIES))
# print(sort_by_urgency(DELIVERIES))