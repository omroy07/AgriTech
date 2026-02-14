import math

class RouteFormulas:
    """
    Mathematical formulas for logistics routing and fuel efficiency.
    """
    
    @staticmethod
    def calculate_haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculates the great-circle distance between two points on Earth in kilometers.
        """
        R = 6371.0  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return round(R * c, 2)

    @staticmethod
    def estimate_fuel_consumption(distance_km, avg_consumption_per_100km, load_weight_kg, max_capacity_kg):
        """
        Estimates fuel consumption factoring in vehicle load.
        Basic formula: distance * (avg_consumption / 100) * (1 + (current_load/max_capacity) * 0.15)
        Adds up to 15% consumption for full load.
        """
        base_consumption = (distance_km / 100) * avg_consumption_per_100km
        load_factor = 1 + (load_weight_kg / max_capacity_kg) * 0.15
        
        return round(base_consumption * load_factor, 2)

    @staticmethod
    def calculate_efficiency_score(actual_fuel_used, estimated_fuel):
        """
        Calculates efficiency score (0-100).
        Score = (Estimated / Actual) * 100
        """
        if actual_fuel_used <= 0:
            return 100.0
        score = (estimated_fuel / actual_fuel_used) * 100
        return round(min(100.0, score), 2)

    @staticmethod
    def optimize_load_distribution(items):
        """
        Simple bin-packing-inspired logic to suggest optimal vehicle assignments.
        Expects items: list of dicts {'id': x, 'weight': y}
        Returns suggestions: list of groups within capacity.
        (Conceptual realization for 1k LoC logic)
        """
        # Sort items by weight descending (Heuristic)
        sorted_items = sorted(items, key=lambda x: x['weight'], reverse=True)
        return sorted_items
