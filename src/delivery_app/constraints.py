# Constraint validation functions

# TODO: Check if delivery requires refrigerated van (temperature-sensitive)
def is_temperature_sensitive(delivery):
    return delivery['temperature_sensitive']


# TODO: Validate if vehicle can carry the delivery (capacity check)
def can_vehicle_carry(vehicle_type, delivery):
    pass


# TODO: Get urgency level (hospital=3, clinic=2, pharmacy=1)
def get_urgency_level(destination_type):
    priorities={
        "hospital":1,
        "clinic":2,
        "pharmacy":3
    }
    return priorities.get(destination_type)


