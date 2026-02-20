from datetime import datetime
from backend.extensions import db
from backend.models.logistics_v2 import DriverProfile, DeliveryVehicle, TransportRoute, FuelLog
from backend.utils.route_formulas import RouteFormulas
import logging

logger = logging.getLogger(__name__)

class LogisticsService:
    @staticmethod
    def create_dispatch(driver_id, vehicle_id, origin, destination, cargo_weight, coords=None, **kwargs):
        """
        Orchestrates the creation of a new transport route.
        """
        try:
            driver = DriverProfile.query.get(driver_id)
            vehicle = DeliveryVehicle.query.get(vehicle_id)
            
            if not driver or driver.status != 'AVAILABLE':
                return None, "Driver not available"
            if not vehicle or vehicle.status != 'IDLE':
                return None, "Vehicle not available"
            
            if cargo_weight > vehicle.capacity_kg:
                return None, f"Cargo exceeds vehicle capacity of {vehicle.capacity_kg}kg"

            # Bio-Security Autonomous Shutdown (L3-1596)
            from backend.models.traceability import SupplyBatch
            # Assuming dispatch is linked to a batch record
            batch_id = kwargs.get('batch_id')
            if batch_id:
                batch = SupplyBatch.query.get(batch_id)
                if not batch or not batch.bio_clearance_hash:
                    return None, "BIO-SECURITY ALERT: Batch lacks Bio-Clearance Hash. Logistics path BLOCKED."
                
                # Verify hash (Optional deeper check)
                if batch.quarantine_status != 'CLEAN':
                    return None, "BIO-SECURITY ALERT: Batch is under QUARANTINE. Logistics path BLOCKED."

            # Calculate distance if coords provided
            est_distance = 0
            if coords and 'origin' in coords and 'dest' in coords:
                o = coords['origin']
                d = coords['dest']
                est_distance = RouteFormulas.calculate_haversine_distance(o[0], o[1], d[0], d[1])

            route = TransportRoute(
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                origin=origin,
                destination=destination,
                origin_coords=f"{coords['origin'][0]},{coords['origin'][1]}" if coords else None,
                destination_coords=f"{coords['dest'][0]},{coords['dest'][1]}" if coords else None,
                estimated_distance=est_distance,
                cargo_weight=cargo_weight,
                status='PENDING'
            )
            
            # Update statuses
            driver.status = 'ON_TRIP'
            vehicle.status = 'ACTIVE'
            
            db.session.add(route)
            db.session.commit()
            return route, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def start_route(route_id):
        """Marks a route as in-transit."""
        route = TransportRoute.query.get(route_id)
        if not route or route.status != 'PENDING':
            return False, "Route cannot be started"
        
        route.status = 'IN_TRANSIT'
        route.start_time = datetime.utcnow()
        db.session.commit()
        return True, None

    @staticmethod
    def complete_route(route_id, actual_distance):
        """Finalizes a route and calculates metrics."""
        try:
            route = TransportRoute.query.get(route_id)
            if not route or route.status != 'IN_TRANSIT':
                return False, "Route not in transit"
            
            route.status = 'COMPLETED'
            route.end_time = datetime.utcnow()
            route.actual_distance = actual_distance
            
            # Update driver & vehicle
            driver = DriverProfile.query.get(route.driver_id)
            vehicle = DeliveryVehicle.query.get(route.vehicle_id)
            
            driver.status = 'AVAILABLE'
            driver.total_trips += 1
            
            vehicle.status = 'IDLE'
            vehicle.mileage += actual_distance
            
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def record_fuel(vehicle_id, quantity, cost, mileage):
        """Logs fuel refill information."""
        log = FuelLog(vehicle_id=vehicle_id, fuel_quantity=quantity, cost=cost, mileage_at_refill=mileage)
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_fleet_status():
        """Aggregates overview of current fleet state."""
        total_vehicles = DeliveryVehicle.query.count()
        active_vehicles = DeliveryVehicle.query.filter_by(status='ACTIVE').count()
        maintenance_vehicles = DeliveryVehicle.query.filter_by(status='MAINTENANCE').count()
        
        return {
            'total': total_vehicles,
            'active': active_vehicles,
            'maintenance': maintenance_vehicles,
            'utilization': round((active_vehicles / total_vehicles * 100), 2) if total_vehicles > 0 else 0
        }
