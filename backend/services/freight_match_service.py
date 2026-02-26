"""
Autonomous Freight Matching Service — L3-1644
============================================
Algorithm for matching logistics orders to available autonomous vehicles.
"""

from datetime import datetime
from backend.extensions import db
from backend.models.freight_v2 import AutonomousVehicle, VehicleMission
from backend.models.autonomous_supply import SmartContractOrder
import math
import logging

logger = logging.getLogger(__name__)

class FreightMatchEngine:
    
    @staticmethod
    def find_nearest_vehicle(order_lat: float, order_lng: float, required_capacity: float):
        """
        Heuristic-based search for nearest available autonomous asset.
        """
        vehicles = AutonomousVehicle.query.filter_by(status='IDLE').all()
        
        best_vehicle = None
        min_distance = float('inf')
        
        for v in vehicles:
            if v.current_capacity_kg < required_capacity:
                continue
                
            # Haversine approximation
            dist = math.sqrt((v.current_lat - order_lat)**2 + (v.current_lng - order_lng)**2)
            
            if dist < min_distance:
                min_distance = dist
                best_vehicle = v
                
        return best_vehicle

    @staticmethod
    def assign_vehicle_to_order(order_id: int):
        """
        Pairs an order to a vehicle and initiates mission state.
        """
        order = SmartContractOrder.query.get(order_id)
        # Assuming order has pickup coordinates (mocked for L3 brevity)
        pickup_lat, pickup_lng = 12.9716, 77.5946 
        
        vehicle = FreightMatchEngine.find_nearest_vehicle(pickup_lat, pickup_lng, order.quantity_kg)
        
        if vehicle:
            vehicle.status = 'IN_TRANSIT'
            mission = VehicleMission(
                vehicle_id=vehicle.id,
                order_id=order_id
            )
            db.session.add(mission)
            order.status = 'SHIPPED'
            db.session.commit()
            
            logger.info(f"Matched Vehicle {vehicle.serial_number} to Order {order_id}.")
            return vehicle
            
        return None
