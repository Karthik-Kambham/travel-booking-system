def search_destinations(city):
    travel_data = {
        "Goa": {
            "country": "India",
            "description": "Beautiful beaches and relaxing holidays",
            "price": 15000
        },
        "Manali": {
            "country": "India",
            "description": "Mountains, snow and adventure",
            "price": 12000
        },
        "Dubai": {
            "country": "UAE",
            "description": "Luxury, shopping and modern attractions",
            "price": 45000
        },
        "Kerala": {
            "country": "India",
            "description": "Backwaters, nature and peaceful destinations",
            "price": 10000
        },
        "Bali": {
            "country": "Indonesia",
            "description": "Beautiful beaches, temples and island adventures",
            "price": 40000
        },
        "Paris": {
            "country": "France",
            "description": "Famous landmarks, culture and attractions",
            "price": 80000
        }
    }
    return travel_data.get(city)

def get_destination_names():
    return [
        "Goa",
        "Manali",
        "Dubai",
        "Kerala",
        "Bali",
        "Paris"
    ]

def get_destination_details(city):
    details = search_destinations(city)
    if details:
        return {
            "destination": city,
            "country": details["country"],
            "description": details["description"],
            "price": details["price"],  # FIXED: app.py expects this key
            "estimated_price": details["price"]
        }
    return None

# -----------------------------------
# 2. TRANSPORT SEARCH - DEMO API
# -----------------------------------

def search_transport(transport_type, source, destination, travel_date):
    """
    Returns predefined demo transport options.
    This is not a live transport API - works offline.
    """

    if not source or not destination:
        return []

    if source.strip().lower() == destination.strip().lower():
        return []

    transport_type = transport_type.strip().lower()

    transport_data = {
        "flight": [
            {
                "operator": "Demo Airways",
                "departure": "08:00 AM",
                "arrival": "10:15 AM",
                "duration": "2h 15m",
                "price": 4500
            },
            {
                "operator": "Sky Travel",
                "departure": "01:30 PM",
                "arrival": "03:45 PM",
                "duration": "2h 15m",
                "price": 5200
            }
        ],
        "train": [
            {
                "operator": "Demo Express",
                "departure": "06:00 AM",
                "arrival": "02:00 PM",
                "duration": "8h",
                "price": 850
            },
            {
                "operator": "City Superfast",
                "departure": "09:00 PM",
                "arrival": "05:30 AM",
                "duration": "8h 30m",
                "price": 1100
            }
        ],
        "bus": [
            {
                "operator": "Demo Travels",
                "departure": "07:00 AM",
                "arrival": "01:00 PM",
                "duration": "6h",
                "price": 700
            },
            {
                "operator": "Comfort Bus",
                "departure": "10:00 PM",
                "arrival": "04:30 AM",
                "duration": "6h 30m",
                "price": 950
            }
        ]
    }

    if transport_type not in transport_data:
        return []

    results = []
    for item in transport_data[transport_type]:
        results.append({
            "transport_type": transport_type.title(),
            "source": source.strip(),
            "destination": destination.strip(),
            "travel_date": str(travel_date),
            "operator": item["operator"],
            "departure": item["departure"],
            "arrival": item["arrival"],
            "duration": item["duration"],
            "price": item["price"]
        })
    return results

def search_flights(source, destination, travel_date):
    return search_transport("flight", source, destination, travel_date)

def search_trains(source, destination, travel_date):
    return search_transport("train", source, destination, travel_date)

def search_buses(source, destination, travel_date):
    return search_transport("bus", source, destination, travel_date)