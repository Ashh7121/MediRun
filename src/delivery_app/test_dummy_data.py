"""
Dummy data for testing delivery optimization algorithm
Run from terminal: python test_dummy_data.py
"""

# Sample warehouse location
WAREHOUSE = {
    "name": "Ivry-sur-Seine warehouse",
    "address": "123 rue de l'Industrie, 94200 Ivry-sur-Seine",
    "lat": 48.7142,
    "lng": 2.3719
}

# Sample drivers
DRIVERS = [
    {"id": 1, "name": "Marc", "van_type": "small"},
    {"id": 2, "name": "Luc", "van_type": "big"},
    {"id": 3, "name": "Ahmed", "van_type": "small"},
    {"id": 4, "name": "Sophie D.", "van_type": "refrigerated"},
    {"id": 5, "name": "Jean", "van_type": "big"}
]

# Sample deliveries for a typical day
DELIVERIES = [
    {
        "id": 1,
        "destination_type": "hospital",
        "location": {"name": "Hôpital Saint-Jean", "address": "12 rue des Lilas, 75013 Paris", "lat": 48.8238, "lng": 2.3575},
        "temperature_sensitive": False,
        "priority": "critical",
        "deadline": "09:00"
    },
    {
        "id": 2,
        "destination_type": "clinic",
        "location": {"name": "Clinique Pasteur", "address": "18 boulevard Pasteur, 75015 Paris", "lat": 48.8348, "lng": 2.3148},
        "temperature_sensitive": False,
        "priority": "high",
        "deadline": "12:00"
    },
    {
        "id": 3,
        "destination_type": "clinic",
        "location": {"name": "Clinique Montsouris", "address": "42 avenue Reille, 75014 Paris", "lat": 48.8176, "lng": 2.3561},
        "temperature_sensitive": True,  # Medicines need refrigeration
        "priority": "high",
        "deadline": "14:00"
    },
    {
        "id": 4,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Centrale", "address": "3 avenue Gambetta, 75020 Paris", "lat": 48.8707, "lng": 2.3968},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "18:00"
    },
    {
        "id": 5,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie République", "address": "6 place de la République, 75011 Paris", "lat": 48.8667, "lng": 2.3624},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "18:00"
    },
    {
        "id": 6,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Voltaire", "address": "91 boulevard Voltaire, 75011 Paris", "lat": 48.8573, "lng": 2.3748},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "18:00"
    },
    {
        "id": 7,
        "destination_type": "clinic",
        "location": {"name": "Clinique Saint-Michel", "address": "9 rue Saint-Michel, 75005 Paris", "lat": 48.8507, "lng": 2.3439},
        "temperature_sensitive": True,  # Vaccines need cold chain
        "priority": "high",
        "deadline": "15:00"
    },
    {
        "id": 8,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Italie", "address": "112 avenue d'Italie, 75013 Paris", "lat": 48.8256, "lng": 2.3562},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "17:00"
    },
    {
        "id": 9,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie du Centre", "address": "25 rue Victor Hugo, 94200 Ivry-sur-Seine", "lat": 48.7165, "lng": 2.3812},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "16:00"
    },
    {
        "id": 10,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie des Lilas", "address": "7 rue de Paris, 93260 Les Lilas", "lat": 48.8746, "lng": 2.4193},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "19:00"
    }
]

# Mock distances from warehouse to each delivery (in km)
# TODO: Replace with actual Google Maps API calls
MOCK_DISTANCES_FROM_WAREHOUSE = {
    1: 8.5,    # Hospital
    2: 12.3,   # Clinic Pasteur
    3: 11.8,   # Clinic Montsouris
    4: 15.2,   # Pharmacy Centrale
    5: 14.1,   # Pharmacy République
    6: 13.9,   # Pharmacy Voltaire
    7: 10.5,   # Clinic Saint-Michel
    8: 9.2,    # Pharmacy Italie
    9: 1.5,    # Pharmacy du Centre (very close, near warehouse)
    10: 3.8    # Pharmacy des Lilas
}


def print_dummy_data():
    """Test function to verify dummy data loads correctly"""
    print("=== WAREHOUSE ===")
    print(WAREHOUSE)
    print("\n=== DRIVERS ===")
    for driver in DRIVERS:
        print(driver)
    print("\n=== SAMPLE DELIVERIES ===")
    for delivery in DELIVERIES:
        print(f"ID: {delivery['id']}, Type: {delivery['destination_type']}, Location: {delivery['location']['name']}, Temp Sensitive: {delivery['temperature_sensitive']}")


if __name__ == "__main__":
    print_dummy_data()
