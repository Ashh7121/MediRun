"""
Dummy data for testing delivery optimization algorithm
Run from terminal: python test_dummy_data.py
"""

# Sample warehouse location
WAREHOUSE = {
    "name": "MediRun Warehouse",
    "address": "18 rue Jules Vanzuppe, 94200 Ivry-sur-Seine",
    "lat": 48.7165,
    "lng": 2.3812
}

# Sample drivers
DRIVERS = [
    {"id": 1, "name": "Marc", "van_type": "small"},
    {"id": 2, "name": "Luc", "van_type": "big"},
    {"id": 3, "name": "Ahmed", "van_type": "small"},
    {"id": 4, "name": "Sophie D.", "van_type": "refrigerated"},
    {"id": 5, "name": "Jean", "van_type": "big"}
]

# Sample deliveries for a typical day (~60 deliveries)
DELIVERIES = [
    # Original core addresses
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
        "temperature_sensitive": True,
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
        "temperature_sensitive": True,
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
    },
    # Additional pharmacies - Paris 11th (short distance cluster)
    {
        "id": 11,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Beaumont", "address": "45 rue Beaumont, 75011 Paris", "lat": 48.8645, "lng": 2.3701},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:00"
    },
    {
        "id": 12,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Oberkampf", "address": "78 rue Oberkampf, 75011 Paris", "lat": 48.8660, "lng": 2.3779},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:30"
    },
    {
        "id": 13,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Menilmontant", "address": "156 rue Menilmontant, 75020 Paris", "lat": 48.8704, "lng": 2.3864},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "12:30"
    },
    {
        "id": 14,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Bastille", "address": "12 rue de Lappe, 75011 Paris", "lat": 48.8527, "lng": 2.3740},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "13:00"
    },
    {
        "id": 15,
        "destination_type": "clinic",
        "location": {"name": "Clinique Belleville", "address": "22 rue Denoyez, 75020 Paris", "lat": 48.8729, "lng": 2.3891},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "14:30"
    },
    # Paris 13th cluster
    {
        "id": 16,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Gobelins", "address": "85 rue Mouffetard, 75005 Paris", "lat": 48.8387, "lng": 2.3515},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "10:00"
    },
    {
        "id": 17,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Butte aux Cailles", "address": "31 rue de la Butte aux Cailles, 75013 Paris", "lat": 48.8290, "lng": 2.3489},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "10:30"
    },
    {
        "id": 18,
        "destination_type": "clinic",
        "location": {"name": "Clinique Tolbiac", "address": "45 rue Tolbiac, 75013 Paris", "lat": 48.8310, "lng": 2.3643},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "11:00"
    },
    {
        "id": 19,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Nationale", "address": "2 place Nationale, 75013 Paris", "lat": 48.8321, "lng": 2.3748},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:45"
    },
    {
        "id": 20,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Maison Blanche", "address": "167 boulevard de Masséna, 75013 Paris", "lat": 48.8198, "lng": 2.3654},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "13:15"
    },
    # Ivry-sur-Seine cluster
    {
        "id": 21,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Quai", "address": "12 quai de la Marne, 94200 Ivry-sur-Seine", "lat": 48.7134, "lng": 2.3891},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "08:00"
    },
    {
        "id": 22,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Palais", "address": "89 rue Palais, 94200 Ivry-sur-Seine", "lat": 48.7198, "lng": 2.3756},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "08:45"
    },
    {
        "id": 23,
        "destination_type": "clinic",
        "location": {"name": "Clinique Ivry", "address": "56 avenue du Docteur Ingard, 94200 Ivry-sur-Seine", "lat": 48.7210, "lng": 2.3634},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "09:30"
    },
    # Les Lilas cluster
    {
        "id": 24,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Mairie", "address": "45 avenue de la République, 93260 Les Lilas", "lat": 48.8768, "lng": 2.4156},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "15:00"
    },
    {
        "id": 25,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Gare", "address": "78 rue Belgrand, 93260 Les Lilas", "lat": 48.8721, "lng": 2.4089},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "15:45"
    },
    # Additional Paris 15th
    {
        "id": 26,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Segur", "address": "23 rue Cler, 75015 Paris", "lat": 48.8530, "lng": 2.3051},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "12:15"
    },
    {
        "id": 27,
        "destination_type": "clinic",
        "location": {"name": "Clinique Sèvres", "address": "34 rue Sèvres, 75006 Paris", "lat": 48.8478, "lng": 2.3290},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "13:30"
    },
    # Additional Paris 20th
    {
        "id": 28,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Père-Lachaise", "address": "114 rue du Père-Lachaise, 75020 Paris", "lat": 48.8668, "lng": 2.3978},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "14:00"
    },
    {
        "id": 29,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Vitruve", "address": "67 rue Vitruve, 75020 Paris", "lat": 48.8714, "lng": 2.4014},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "14:30"
    },
    # Bulk additions - more Paris 11th locations
    {
        "id": 30,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Chemin Vert", "address": "71 rue du Chemin Vert, 75011 Paris", "lat": 48.8617, "lng": 2.3823},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "09:00"
    },
    {
        "id": 31,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Breguet", "address": "34 rue Breguet, 75011 Paris", "lat": 48.8589, "lng": 2.3794},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "09:30"
    },
    {
        "id": 32,
        "destination_type": "clinic",
        "location": {"name": "Clinique Rochebrune", "address": "17 rue Rochebrune, 75011 Paris", "lat": 48.8541, "lng": 2.3656},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "10:15"
    },
    {
        "id": 33,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Parmentier", "address": "82 avenue Parmentier, 75011 Paris", "lat": 48.8629, "lng": 2.3867},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:00"
    },
    {
        "id": 34,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Lyon", "address": "65 rue de Lyon, 75012 Paris", "lat": 48.8468, "lng": 2.3848},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:45"
    },
    # More Paris 13th
    {
        "id": 35,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Leonidas", "address": "29 avenue Leonidas, 75013 Paris", "lat": 48.8272, "lng": 2.3621},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "12:00"
    },
    {
        "id": 36,
        "destination_type": "clinic",
        "location": {"name": "Clinique Davout", "address": "8 avenue Davout, 75013 Paris", "lat": 48.8346, "lng": 2.3743},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "13:00"
    },
    {
        "id": 37,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Glacière", "address": "52 rue de la Glacière, 75013 Paris", "lat": 48.8257, "lng": 2.3421},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "14:00"
    },
    {
        "id": 38,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Bertha", "address": "18 rue Bertha, 75013 Paris", "lat": 48.8324, "lng": 2.3501},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "14:45"
    },
    # More Ivry cluster
    {
        "id": 39,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Nodier", "address": "3 rue Nodier, 94200 Ivry-sur-Seine", "lat": 48.7146, "lng": 2.3701},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "15:30"
    },
    {
        "id": 40,
        "destination_type": "clinic",
        "location": {"name": "Clinique Landy", "address": "121 rue Landy, 94200 Ivry-sur-Seine", "lat": 48.7232, "lng": 2.3834},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "16:00"
    },
    # More Les Lilas
    {
        "id": 41,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Carnot", "address": "88 avenue Carnot, 93260 Les Lilas", "lat": 48.8745, "lng": 2.4245},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "16:30"
    },
    # Suburban reaches
    {
        "id": 42,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Fontenay", "address": "42 rue Victor Basch, 94120 Fontenay-sous-Bois", "lat": 48.8476, "lng": 2.4801},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "17:00"
    },
    {
        "id": 43,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Montreuil", "address": "67 avenue Jean Lolive, 93100 Montreuil", "lat": 48.8618, "lng": 2.4412},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "17:30"
    },
    # Back to dense central Paris
    {
        "id": 44,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Marais", "address": "35 rue Turenne, 75004 Paris", "lat": 48.8587, "lng": 2.3651},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "10:00"
    },
    {
        "id": 45,
        "destination_type": "clinic",
        "location": {"name": "Clinique Vieille du Temple", "address": "44 rue Vieille du Temple, 75004 Paris", "lat": 48.8599, "lng": 2.3627},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "10:30"
    },
    # More Paris 5th
    {
        "id": 46,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Seine", "address": "56 rue de Seine, 75006 Paris", "lat": 48.8556, "lng": 2.3365},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:00"
    },
    {
        "id": 47,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Odeon", "address": "23 rue de l'Odéon, 75006 Paris", "lat": 48.8505, "lng": 2.3403},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "11:30"
    },
    # Paris 14th expansion
    {
        "id": 48,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Daguerre", "address": "80 rue Daguerre, 75014 Paris", "lat": 48.8306, "lng": 2.3269},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "12:00"
    },
    {
        "id": 49,
        "destination_type": "clinic",
        "location": {"name": "Clinique Mouton-Duvernet", "address": "15 rue Mouton-Duvernet, 75014 Paris", "lat": 48.8336, "lng": 2.3341},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "13:00"
    },
    # Paris 12th additions
    {
        "id": 50,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Nation", "address": "91 rue de Bercy, 75012 Paris", "lat": 48.8417, "lng": 2.3967},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "13:30"
    },
    {
        "id": 51,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Ledru-Rollin", "address": "24 rue Ledru-Rollin, 75012 Paris", "lat": 48.8469, "lng": 2.3751},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "14:00"
    },
    # Additional high-priority medical stops
    {
        "id": 52,
        "destination_type": "clinic",
        "location": {"name": "Clinique Urgence 11", "address": "91 rue Amelot, 75011 Paris", "lat": 48.8594, "lng": 2.3721},
        "temperature_sensitive": True,
        "priority": "critical",
        "deadline": "09:45"
    },
    {
        "id": 53,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Popincourt", "address": "73 rue Popincourt, 75011 Paris", "lat": 48.8606, "lng": 2.3795},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "15:00"
    },
    {
        "id": 54,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Ledoux", "address": "62 rue Ledoux, 75020 Paris", "lat": 48.8682, "lng": 2.3932},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "15:30"
    },
    {
        "id": 55,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Roquette", "address": "128 rue de la Roquette, 75011 Paris", "lat": 48.8539, "lng": 2.3869},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "16:00"
    },
    {
        "id": 56,
        "destination_type": "clinic",
        "location": {"name": "Clinique Bagnolet", "address": "55 rue Saint-Fargeau, 75020 Paris", "lat": 48.8714, "lng": 2.4085},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "16:30"
    },
    {
        "id": 57,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Avron", "address": "89 avenue Avron, 75020 Paris", "lat": 48.8773, "lng": 2.4072},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "17:00"
    },
    {
        "id": 58,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Vinces", "address": "15 rue des Vinces, 75020 Paris", "lat": 48.8747, "lng": 2.3952},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "17:30"
    },
    {
        "id": 59,
        "destination_type": "clinic",
        "location": {"name": "Clinique Couronnes", "address": "35 rue des Couronnes, 75020 Paris", "lat": 48.8723, "lng": 2.3897},
        "temperature_sensitive": True,
        "priority": "high",
        "deadline": "18:00"
    },
    {
        "id": 60,
        "destination_type": "pharmacy",
        "location": {"name": "Pharmacie Sorbier", "address": "42 rue Sorbier, 75020 Paris", "lat": 48.8749, "lng": 2.3928},
        "temperature_sensitive": False,
        "priority": "normal",
        "deadline": "18:30"
    }
]

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
