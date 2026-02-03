"""
Geospatial Service for Pest & Disease Early Warning System (GEWS)
Handles spatial clustering, outbreak detection, and radius-based queries
"""

import math
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from sqlalchemy import func, and_, or_
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint, ST_AsText
from backend.extensions import db
from backend.models import DiseaseIncident, OutbreakZone, User, OutbreakAlert
from backend.utils.logger import logger


class GeospatialService:
    """Service for geospatial operations and outbreak detection"""
    
    # Constants
    OUTBREAK_THRESHOLD = 3  # Minimum incidents to declare outbreak
    CLUSTERING_RADIUS_KM = 50  # Default clustering radius
    EARTH_RADIUS_KM = 6371  # Earth's radius in kilometers
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return GeospatialService.EARTH_RADIUS_KM * c
    
    @staticmethod
    def find_incidents_in_radius(center_lat: float, center_lon: float, 
                                 radius_km: float, 
                                 disease_name: Optional[str] = None,
                                 crop_affected: Optional[str] = None,
                                 days_back: int = 30) -> List[DiseaseIncident]:
        """
        Find all incidents within a radius of a center point.
        
        Args:
            center_lat, center_lon: Center point coordinates
            radius_km: Search radius in kilometers
            disease_name: Optional filter by disease name
            crop_affected: Optional filter by crop
            days_back: Only include incidents from last N days
            
        Returns:
            List of DiseaseIncident objects
        """
        try:
            # Convert radius to meters for PostGIS (if using PostGIS)
            radius_meters = radius_km * 1000
            
            # Create center point
            center_point = func.ST_SetSRID(func.ST_MakePoint(center_lon, center_lat), 4326)
            
            # Build query with spatial filter
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            query = DiseaseIncident.query.filter(
                and_(
                    func.ST_DWithin(
                        func.ST_Transform(DiseaseIncident.location, 4326),
                        func.ST_Transform(center_point, 4326),
                        radius_meters,
                        True  # Use spheroid for accurate distance
                    ),
                    DiseaseIncident.reported_at >= cutoff_date,
                    DiseaseIncident.status.in_(['reported', 'verified'])
                )
            )
            
            # Add optional filters
            if disease_name:
                query = query.filter(DiseaseIncident.disease_name == disease_name)
            
            if crop_affected:
                query = query.filter(DiseaseIncident.crop_affected == crop_affected)
            
            incidents = query.all()
            
            # Fallback to Python calculation if PostGIS not available
            if not incidents:
                incidents = GeospatialService._find_incidents_in_radius_fallback(
                    center_lat, center_lon, radius_km, disease_name, crop_affected, days_back
                )
            
            return incidents
        
        except Exception as e:
            logger.warning(f"PostGIS query failed, using fallback: {str(e)}")
            return GeospatialService._find_incidents_in_radius_fallback(
                center_lat, center_lon, radius_km, disease_name, crop_affected, days_back
            )
    
    @staticmethod
    def _find_incidents_in_radius_fallback(center_lat: float, center_lon: float,
                                           radius_km: float,
                                           disease_name: Optional[str] = None,
                                           crop_affected: Optional[str] = None,
                                           days_back: int = 30) -> List[DiseaseIncident]:
        """
        Fallback method using Python calculations when PostGIS is unavailable.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = DiseaseIncident.query.filter(
            and_(
                DiseaseIncident.reported_at >= cutoff_date,
                DiseaseIncident.status.in_(['reported', 'verified'])
            )
        )
        
        if disease_name:
            query = query.filter(DiseaseIncident.disease_name == disease_name)
        
        if crop_affected:
            query = query.filter(DiseaseIncident.crop_affected == crop_affected)
        
        all_incidents = query.all()
        
        # Filter by distance using Haversine
        nearby_incidents = []
        for incident in all_incidents:
            distance = GeospatialService.calculate_distance(
                center_lat, center_lon,
                incident.latitude, incident.longitude
            )
            if distance <= radius_km:
                nearby_incidents.append(incident)
        
        return nearby_incidents
    
    @staticmethod
    def detect_outbreak_clusters(radius_km: float = CLUSTERING_RADIUS_KM,
                                 min_incidents: int = OUTBREAK_THRESHOLD,
                                 days_back: int = 30) -> List[Dict]:
        """
        Detect outbreak clusters by analyzing spatial distribution of incidents.
        
        Args:
            radius_km: Clustering radius
            min_incidents: Minimum incidents to declare outbreak
            days_back: Only analyze incidents from last N days
            
        Returns:
            List of cluster dictionaries with outbreak information
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get recent incidents
        incidents = DiseaseIncident.query.filter(
            and_(
                DiseaseIncident.reported_at >= cutoff_date,
                DiseaseIncident.status.in_(['reported', 'verified']),
                DiseaseIncident.outbreak_zone_id.is_(None)  # Not yet assigned to outbreak
            )
        ).order_by(DiseaseIncident.reported_at.desc()).all()
        
        if len(incidents) < min_incidents:
            return []
        
        # Group incidents by disease and crop
        incident_groups = defaultdict(list)
        for incident in incidents:
            key = (incident.disease_name, incident.crop_affected)
            incident_groups[key].append(incident)
        
        clusters = []
        
        # Analyze each group for spatial clustering
        for (disease_name, crop_affected), group_incidents in incident_groups.items():
            if len(group_incidents) < min_incidents:
                continue
            
            # DBSCAN-like clustering
            cluster_candidates = GeospatialService._find_dense_clusters(
                group_incidents, radius_km, min_incidents
            )
            
            for cluster in cluster_candidates:
                # Calculate cluster center (centroid)
                center_lat = sum(inc.latitude for inc in cluster) / len(cluster)
                center_lon = sum(inc.longitude for inc in cluster) / len(cluster)
                
                # Calculate severity level
                severity_counts = defaultdict(int)
                for inc in cluster:
                    severity_counts[inc.severity] += 1
                
                # Determine overall severity
                if severity_counts.get('critical', 0) > 0:
                    severity_level = 'critical'
                elif severity_counts.get('high', 0) >= len(cluster) / 2:
                    severity_level = 'high'
                elif severity_counts.get('medium', 0) >= len(cluster) / 2:
                    severity_level = 'medium'
                else:
                    severity_level = 'low'
                
                clusters.append({
                    'disease_name': disease_name,
                    'crop_affected': crop_affected,
                    'center_lat': center_lat,
                    'center_lon': center_lon,
                    'radius_km': radius_km,
                    'incident_count': len(cluster),
                    'incidents': cluster,
                    'severity_level': severity_level,
                    'total_affected_area': sum(inc.affected_area_hectares or 0 for inc in cluster)
                })
        
        return clusters
    
    @staticmethod
    def _find_dense_clusters(incidents: List[DiseaseIncident], 
                            radius_km: float, 
                            min_incidents: int) -> List[List[DiseaseIncident]]:
        """
        Find dense clusters using a simplified DBSCAN approach.
        """
        visited = set()
        clusters = []
        
        for incident in incidents:
            if incident.id in visited:
                continue
            
            # Find all neighbors within radius
            neighbors = []
            for other in incidents:
                if other.id == incident.id:
                    continue
                
                distance = GeospatialService.calculate_distance(
                    incident.latitude, incident.longitude,
                    other.latitude, other.longitude
                )
                
                if distance <= radius_km:
                    neighbors.append(other)
            
            # If enough neighbors, create cluster
            if len(neighbors) + 1 >= min_incidents:
                cluster = [incident] + neighbors
                clusters.append(cluster)
                
                # Mark as visited
                visited.add(incident.id)
                for neighbor in neighbors:
                    visited.add(neighbor.id)
        
        return clusters
    
    @staticmethod
    def create_outbreak_zone(cluster_data: Dict) -> OutbreakZone:
        """
        Create an outbreak zone from cluster data.
        
        Args:
            cluster_data: Dictionary with cluster information
            
        Returns:
            Created OutbreakZone object
        """
        # Generate unique zone ID
        zone_id = GeospatialService._generate_zone_id(
            cluster_data['disease_name'],
            cluster_data['center_lat'],
            cluster_data['center_lon']
        )
        
        # Create outbreak zone
        zone = OutbreakZone(
            zone_id=zone_id,
            disease_name=cluster_data['disease_name'],
            crop_affected=cluster_data['crop_affected'],
            severity_level=cluster_data['severity_level'],
            center_latitude=cluster_data['center_lat'],
            center_longitude=cluster_data['center_lon'],
            radius_km=cluster_data['radius_km'],
            incident_count=cluster_data['incident_count'],
            total_affected_area=cluster_data.get('total_affected_area', 0),
            status='active',
            risk_level=GeospatialService._calculate_risk_level(cluster_data)
        )
        
        zone.set_center_location(cluster_data['center_lat'], cluster_data['center_lon'])
        
        db.session.add(zone)
        db.session.flush()  # Get zone ID
        
        # Associate incidents with outbreak zone
        for incident in cluster_data['incidents']:
            incident.outbreak_zone_id = zone.id
        
        db.session.commit()
        
        logger.info(f"Created outbreak zone {zone_id} with {cluster_data['incident_count']} incidents")
        
        return zone
    
    @staticmethod
    def find_farmers_at_risk(outbreak_zone: OutbreakZone, 
                            radius_multiplier: float = 1.5) -> List[Tuple[User, float]]:
        """
        Find farmers whose farms are within risk radius of an outbreak zone.
        
        Args:
            outbreak_zone: OutbreakZone to check
            radius_multiplier: Multiplier for warning radius (default 1.5x)
            
        Returns:
            List of tuples (User, distance_km)
        """
        warning_radius = outbreak_zone.radius_km * radius_multiplier
        
        # Get farmers with registered farm locations
        farmers = User.query.filter(
            and_(
                User.role == 'farmer',
                User.farm_latitude.isnot(None),
                User.farm_longitude.isnot(None)
            )
        ).all()
        
        at_risk_farmers = []
        
        for farmer in farmers:
            distance = GeospatialService.calculate_distance(
                outbreak_zone.center_latitude,
                outbreak_zone.center_longitude,
                farmer.farm_latitude,
                farmer.farm_longitude
            )
            
            if distance <= warning_radius:
                at_risk_farmers.append((farmer, distance))
        
        # Sort by distance (closest first)
        at_risk_farmers.sort(key=lambda x: x[1])
        
        return at_risk_farmers
    
    @staticmethod
    def check_user_in_outbreak_zones(user_id: int) -> List[Tuple[OutbreakZone, float]]:
        """
        Check if a user's farm location is within any active outbreak zones.
        
        Args:
            user_id: User ID to check
            
        Returns:
            List of tuples (OutbreakZone, distance_km) for zones within risk radius
        """
        user = User.query.get(user_id)
        
        if not user or not user.farm_latitude or not user.farm_longitude:
            return []
        
        # Get active outbreak zones
        active_zones = OutbreakZone.query.filter(
            OutbreakZone.status == 'active'
        ).all()
        
        nearby_zones = []
        
        for zone in active_zones:
            distance = GeospatialService.calculate_distance(
                user.farm_latitude,
                user.farm_longitude,
                zone.center_latitude,
                zone.center_longitude
            )
            
            # Include zones within 1.5x radius for early warning
            warning_radius = zone.radius_km * 1.5
            
            if distance <= warning_radius:
                nearby_zones.append((zone, distance))
        
        # Sort by distance (closest first)
        nearby_zones.sort(key=lambda x: x[1])
        
        return nearby_zones
    
    @staticmethod
    def _generate_zone_id(disease_name: str, lat: float, lon: float) -> str:
        """Generate unique zone identifier"""
        unique_str = f"{disease_name}-{lat:.4f}-{lon:.4f}-{datetime.utcnow().isoformat()}"
        hash_obj = hashlib.sha256(unique_str.encode())
        return f"OUTBREAK-{hash_obj.hexdigest()[:12].upper()}"
    
    @staticmethod
    def _calculate_risk_level(cluster_data: Dict) -> str:
        """
        Calculate risk level based on cluster characteristics.
        
        Returns:
            'low', 'medium', 'high', or 'extreme'
        """
        incident_count = cluster_data['incident_count']
        severity_level = cluster_data['severity_level']
        
        # Risk scoring
        if severity_level == 'critical' and incident_count >= 10:
            return 'extreme'
        elif severity_level == 'critical' or incident_count >= 8:
            return 'high'
        elif severity_level == 'high' or incident_count >= 5:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_incidents_geojson(disease_name: Optional[str] = None,
                             crop_affected: Optional[str] = None,
                             days_back: int = 30) -> Dict:
        """
        Get incidents as GeoJSON FeatureCollection for mapping.
        
        Args:
            disease_name: Optional filter by disease
            crop_affected: Optional filter by crop
            days_back: Only include incidents from last N days
            
        Returns:
            GeoJSON FeatureCollection
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = DiseaseIncident.query.filter(
            DiseaseIncident.reported_at >= cutoff_date
        )
        
        if disease_name:
            query = query.filter(DiseaseIncident.disease_name == disease_name)
        
        if crop_affected:
            query = query.filter(DiseaseIncident.crop_affected == crop_affected)
        
        incidents = query.all()
        
        features = [incident.to_geojson_feature() for incident in incidents]
        
        return {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': {
                'count': len(features),
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    @staticmethod
    def get_outbreak_zones_geojson() -> Dict:
        """
        Get outbreak zones as GeoJSON FeatureCollection for mapping.
        
        Returns:
            GeoJSON FeatureCollection
        """
        zones = OutbreakZone.query.filter(
            OutbreakZone.status == 'active'
        ).all()
        
        features = [zone.to_geojson_feature() for zone in zones]
        
        return {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': {
                'count': len(features),
                'generated_at': datetime.utcnow().isoformat()
            }
        }
