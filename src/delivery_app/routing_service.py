# Google Maps API wrapper for routing and distance calculations

# TODO: Initialize Google Maps client with API key
def initialize_maps_client(api_key):
    pass


# TODO: Call Distance Matrix API
# Input: warehouse location + list of delivery locations
# Output: distances and travel times from warehouse to each delivery
def get_distances_from_warehouse(warehouse_location, delivery_locations):
    pass


# TODO: Call Distance Matrix API for distances between all delivery points
# Used for greedy sorting (which delivery is closest to current location?)
def get_distances_between_locations(current_location, potential_next_locations):
    pass


# TODO: Call Directions API to get optimized route
# Input: ordered list of delivery waypoints
# Output: turn-by-turn route, total time, ETAs
def get_optimized_route(warehouse, ordered_deliveries):
    pass
