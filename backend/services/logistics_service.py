"""
Autonomous Farm Logistics & Route Optimization Service
Coordinates harvest pickup, vehicle routing, and cost-sharing for farmers.
"""
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_, func
from extensions import db
from models import LogisticsOrder, User

logger = logging.getLogger(__name__)


class LogisticsService:
    """
    Handles logistics coordination including route optimization,
    cost sharing, and vehicle-farmer matching.
    """
    
    # Pricing constants
    BASE_COST_PER_KM = 2.5  # Currency per km
    COST_PER_TON = 50.0  # Base cost per ton
    MAX_GROUP_DISCOUNT = 0.35  # 35% max discount for grouped routes
    GROUPING_RADIUS_KM = 15  # Max distance to group nearby orders
    
    # Vehicle capacity
    VEHICLE_CAPACITY_TONS = 20
    MAX_ORDERS_PER_ROUTE = 8
    
    @staticmethod
    def create_order(user_id: int, order_data: Dict) -> LogisticsOrder:
        """
        Create a new logistics pickup order.
        
        Args:
            user_id: Farmer user ID
            order_data: Order details including location, crop, quantity
            
        Returns:
            Created LogisticsOrder object
        """
        try:
            # Generate order ID
            order_id = f"LOG-{datetime.utcnow().strftime('%Y%m%d')}-{user_id}-{LogisticsOrder.query.count() + 1:04d}"
            
            order = LogisticsOrder(
                order_id=order_id,
                user_id=user_id,
                crop_type=order_data.get('crop_type', 'unknown'),
                quantity_tons=order_data.get('quantity_tons', 0),
                pickup_location=order_data.get('pickup_location', ''),
                pickup_latitude=order_data.get('pickup_latitude'),
                pickup_longitude=order_data.get('pickup_longitude'),
                destination_location=order_data.get('destination_location', ''),
                destination_latitude=order_data.get('destination_latitude'),
                destination_longitude=order_data.get('destination_longitude'),
                requested_pickup_date=datetime.fromisoformat(order_data['requested_pickup_date']),
                priority=order_data.get('priority', 'NORMAL'),
                special_instructions=order_data.get('special_instructions'),
                requires_refrigeration=order_data.get('requires_refrigeration', False),
                requires_covered_transport=order_data.get('requires_covered_transport', False),
                status='PENDING'
            )
            
            # Calculate base cost
            if order.pickup_latitude and order.pickup_longitude and order.destination_latitude and order.destination_longitude:
                distance = LogisticsService._calculate_distance(
                    order.pickup_latitude, order.pickup_longitude,
                    order.destination_latitude, order.destination_longitude
                )
                order.distance_km = distance
                order.base_cost = (distance * LogisticsService.BASE_COST_PER_KM) + (order.quantity_tons * LogisticsService.COST_PER_TON)
                order.final_cost = order.base_cost  # Will be adjusted by route grouping
            
            db.session.add(order)
            db.session.commit()
            
            logger.info(f"Logistics order created: {order_id} for user {user_id}")
            return order
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating logistics order: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate Haversine distance between two coordinates in km.
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def optimize_routes(date: datetime, region: Optional[str] = None) -> List[Dict]:
        """
        Optimize pickup routes for a specific date using clustering algorithm.
        Groups nearby orders to maximize vehicle utilization and minimize costs.
        
        Args:
            date: Target pickup date
            region: Optional region filter
            
        Returns:
            List of optimized route groups with assigned orders
        """
        try:
            # Get pending orders for the date
            query = LogisticsOrder.query.filter(
                and_(
                    LogisticsOrder.requested_pickup_date.cast(db.Date) == date.date(),
                    LogisticsOrder.status == 'PENDING'
                )
            )
            
            orders = query.all()
            
            if not orders:
                logger.info(f"No pending orders for {date.date()}")
                return []
            
            # Group orders by proximity
            route_groups = LogisticsService._cluster_orders(orders)
            
            # Optimize each route group
            optimized_routes = []
            for group_idx, group_orders in enumerate(route_groups):
                route_id = f"ROUTE-{date.strftime('%Y%m%d')}-{group_idx + 1:03d}"
                
                # Calculate route details
                route_info = LogisticsService._calculate_route_details(route_id, group_orders)
                optimized_routes.append(route_info)
                
                # Update orders with route group
                for order in group_orders:
                    order.route_group_id = route_id
                    order.status = 'SCHEDULED'
                    
                    # Apply cost discount
                    discount_pct = route_info['discount_percentage']
                    order.shared_cost_discount = order.base_cost * (discount_pct / 100)
                    order.final_cost = order.base_cost - order.shared_cost_discount
            
            db.session.commit()
            
            logger.info(f"Route optimization completed: {len(optimized_routes)} routes for {len(orders)} orders")
            return optimized_routes
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error optimizing routes: {str(e)}")
            raise
    
    @staticmethod
    def _cluster_orders(orders: List[LogisticsOrder]) -> List[List[LogisticsOrder]]:
        """
        Cluster orders by proximity and capacity constraints.
        Uses greedy nearest-neighbor approach.
        """
        if not orders:
            return []
        
        # Filter orders with valid coordinates
        valid_orders = [o for o in orders if o.pickup_latitude and o.pickup_longitude]
        
        if not valid_orders:
            logger.warning("No orders with valid coordinates")
            return [[o] for o in orders]  # Return individual orders
        
        clusters = []
        remaining = valid_orders.copy()
        
        while remaining:
            # Start new cluster with first remaining order
            seed = remaining.pop(0)
            cluster = [seed]
            cluster_weight = seed.quantity_tons
            
            # Find nearby orders that fit capacity
            to_remove = []
            for order in remaining[:]:
                # Check proximity
                distance = LogisticsService._calculate_distance(
                    seed.pickup_latitude, seed.pickup_longitude,
                    order.pickup_latitude, order.pickup_longitude
                )
                
                # Check if order can be added to cluster
                if (distance <= LogisticsService.GROUPING_RADIUS_KM and
                    cluster_weight + order.quantity_tons <= LogisticsService.VEHICLE_CAPACITY_TONS and
                    len(cluster) < LogisticsService.MAX_ORDERS_PER_ROUTE):
                    
                    cluster.append(order)
                    cluster_weight += order.quantity_tons
                    to_remove.append(order)
            
            # Remove added orders from remaining
            for order in to_remove:
                remaining.remove(order)
            
            clusters.append(cluster)
        
        # Add orders without coordinates as individual clusters
        invalid_orders = [o for o in orders if not (o.pickup_latitude and o.pickup_longitude)]
        for order in invalid_orders:
            clusters.append([order])
        
        return clusters
    
    @staticmethod
    def _calculate_route_details(route_id: str, orders: List[LogisticsOrder]) -> Dict:
        """
        Calculate route statistics and savings from grouping.
        """
        total_distance = 0
        total_quantity = 0
        total_base_cost = 0
        pickup_points = []
        
        for order in orders:
            total_quantity += order.quantity_tons
            total_base_cost += order.base_cost if order.base_cost else 0
            
            if order.pickup_latitude and order.pickup_longitude:
                pickup_points.append({
                    'order_id': order.order_id,
                    'lat': order.pickup_latitude,
                    'lon': order.pickup_longitude,
                    'location': order.pickup_location
                })
        
        # Calculate TSP-like route (simplified nearest neighbor)
        if len(pickup_points) > 1:
            route_distance = LogisticsService._calculate_route_distance(pickup_points)
            total_distance = route_distance
        
        # Calculate discount based on grouping efficiency
        num_orders = len(orders)
        if num_orders > 1:
            # More orders = higher discount (up to MAX_GROUP_DISCOUNT)
            discount_pct = min(
                LogisticsService.MAX_GROUP_DISCOUNT * 100,
                (num_orders - 1) * 10  # 10% per additional order
            )
        else:
            discount_pct = 0
        
        total_discounted_cost = total_base_cost * (1 - discount_pct / 100)
        total_savings = total_base_cost - total_discounted_cost
        
        return {
            'route_id': route_id,
            'order_count': num_orders,
            'total_quantity_tons': total_quantity,
            'total_distance_km': round(total_distance, 2),
            'total_base_cost': round(total_base_cost, 2),
            'discount_percentage': round(discount_pct, 1),
            'total_discounted_cost': round(total_discounted_cost, 2),
            'total_savings': round(total_savings, 2),
            'avg_savings_per_order': round(total_savings / num_orders, 2) if num_orders > 0 else 0,
            'pickup_points': pickup_points,
            'orders': [o.order_id for o in orders]
        }
    
    @staticmethod
    def _calculate_route_distance(points: List[Dict]) -> float:
        """
        Calculate total route distance using nearest neighbor heuristic.
        """
        if len(points) <= 1:
            return 0
        
        visited = [points[0]]
        unvisited = points[1:]
        total_distance = 0
        
        current = visited[0]
        
        while unvisited:
            # Find nearest unvisited point
            nearest = min(
                unvisited,
                key=lambda p: LogisticsService._calculate_distance(
                    current['lat'], current['lon'],
                    p['lat'], p['lon']
                )
            )
            
            distance = LogisticsService._calculate_distance(
                current['lat'], current['lon'],
                nearest['lat'], nearest['lon']
            )
            
            total_distance += distance
            visited.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return total_distance
    
    @staticmethod
    def assign_vehicle(route_group_id: str, vehicle_data: Dict) -> List[LogisticsOrder]:
        """
        Assign a vehicle and driver to a route group.
        
        Args:
            route_group_id: Route identifier
            vehicle_data: Vehicle and driver details
            
        Returns:
            List of updated orders
        """
        try:
            orders = LogisticsOrder.query.filter_by(route_group_id=route_group_id).all()
            
            if not orders:
                raise ValueError(f"No orders found for route {route_group_id}")
            
            # Assign vehicle to all orders in route
            for order in orders:
                order.transport_vehicle_id = vehicle_data.get('vehicle_id')
                order.driver_name = vehicle_data.get('driver_name')
                order.driver_phone = vehicle_data.get('driver_phone')
                order.scheduled_pickup_date = datetime.fromisoformat(vehicle_data['scheduled_pickup_date'])
                
                # Calculate estimated delivery
                if order.distance_km:
                    avg_speed_kmh = 40  # Average speed
                    travel_hours = order.distance_km / avg_speed_kmh
                    order.estimated_delivery_date = order.scheduled_pickup_date + timedelta(hours=travel_hours)
            
            db.session.commit()
            
            logger.info(f"Vehicle assigned to route {route_group_id}: {vehicle_data.get('vehicle_id')}")
            return orders
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error assigning vehicle: {str(e)}")
            raise
    
    @staticmethod
    def update_order_status(order_id: str, status: str, update_data: Optional[Dict] = None) -> LogisticsOrder:
        """
        Update order status and optional delivery details.
        
        Args:
            order_id: Order identifier
            status: New status (IN_TRANSIT, DELIVERED, etc.)
            update_data: Optional additional data
            
        Returns:
            Updated LogisticsOrder object
        """
        try:
            order = LogisticsOrder.query.filter_by(order_id=order_id).first()
            if not order:
                raise ValueError(f"Order {order_id} not found")
            
            old_status = order.status
            order.status = status
            
            if update_data:
                if 'actual_pickup_date' in update_data:
                    order.actual_pickup_date = datetime.fromisoformat(update_data['actual_pickup_date'])
                
                if 'actual_delivery_date' in update_data:
                    order.actual_delivery_date = datetime.fromisoformat(update_data['actual_delivery_date'])
            
            # Auto-set timestamps based on status
            if status == 'IN_TRANSIT' and not order.actual_pickup_date:
                order.actual_pickup_date = datetime.utcnow()
            
            if status == 'DELIVERED' and not order.actual_delivery_date:
                order.actual_delivery_date = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Order {order_id} status updated: {old_status} -> {status}")
            return order
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating order status: {str(e)}")
            raise
    
    @staticmethod
    def get_orders_by_user(user_id: int, filters: Optional[Dict] = None) -> List[LogisticsOrder]:
        """
        Get logistics orders for a user with optional filters.
        
        Args:
            user_id: User ID
            filters: Optional filters (status, date_range)
            
        Returns:
            List of LogisticsOrder objects
        """
        query = LogisticsOrder.query.filter_by(user_id=user_id)
        
        if filters:
            if 'status' in filters:
                query = query.filter(LogisticsOrder.status == filters['status'])
            
            if 'from_date' in filters:
                from_date = datetime.fromisoformat(filters['from_date'])
                query = query.filter(LogisticsOrder.requested_pickup_date >= from_date)
            
            if 'to_date' in filters:
                to_date = datetime.fromisoformat(filters['to_date'])
                query = query.filter(LogisticsOrder.requested_pickup_date <= to_date)
        
        return query.order_by(LogisticsOrder.requested_pickup_date.desc()).all()
    
    @staticmethod
    def get_route_summary(route_group_id: str) -> Dict:
        """Get summary statistics for a route group."""
        orders = LogisticsOrder.query.filter_by(route_group_id=route_group_id).all()
        
        if not orders:
            return {}
        
        total_quantity = sum(o.quantity_tons for o in orders)
        total_cost = sum(o.final_cost for o in orders if o.final_cost)
        total_savings = sum(o.shared_cost_discount for o in orders if o.shared_cost_discount)
        
        return {
            'route_group_id': route_group_id,
            'total_orders': len(orders),
            'total_quantity_tons': total_quantity,
            'total_cost': round(total_cost, 2),
            'total_savings': round(total_savings, 2),
            'vehicle_id': orders[0].transport_vehicle_id if orders else None,
            'driver': orders[0].driver_name if orders else None,
            'status': orders[0].status if orders else 'UNKNOWN',
            'orders': [o.order_id for o in orders]
        }
    
    @staticmethod
    def get_logistics_analytics(user_id: Optional[int] = None, days: int = 30) -> Dict:
        """Get logistics performance analytics."""
        query = LogisticsOrder.query.filter(
            LogisticsOrder.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        orders = query.all()
        
        total_orders = len(orders)
        completed = sum(1 for o in orders if o.status == 'DELIVERED')
        total_savings = sum(o.shared_cost_discount for o in orders if o.shared_cost_discount)
        total_quantity = sum(o.quantity_tons for o in orders)
        
        # Route efficiency
        routes = {}
        for order in orders:
            if order.route_group_id:
                if order.route_group_id not in routes:
                    routes[order.route_group_id] = []
                routes[order.route_group_id].append(order)
        
        avg_orders_per_route = len(orders) / len(routes) if routes else 0
        
        return {
            'period_days': days,
            'total_orders': total_orders,
            'completed_orders': completed,
            'completion_rate': round(completed / total_orders * 100, 1) if total_orders > 0 else 0,
            'total_quantity_tons': round(total_quantity, 2),
            'total_savings': round(total_savings, 2),
            'avg_savings_per_order': round(total_savings / total_orders, 2) if total_orders > 0 else 0,
            'total_routes': len(routes),
            'avg_orders_per_route': round(avg_orders_per_route, 1),
            'grouped_orders': sum(1 for o in orders if o.route_group_id),
            'grouping_rate': round(sum(1 for o in orders if o.route_group_id) / total_orders * 100, 1) if total_orders > 0 else 0
        }
