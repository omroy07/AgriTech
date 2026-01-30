import os
import json
import numpy as np
# Note: rasterio is recommended for production. For this snippet we use mocking or basic array ops if rasterio missing.
# We will assume rasterio is installed or we fallback.
try:
    import rasterio
    from rasterio import mask
except ImportError:
    rasterio = None

import cv2
from datetime import datetime

class SpatialUtils:
    
    @staticmethod
    def calculate_ndvi(red_band, nir_band):
        """
        Calculate NDVI from Red and NIR bands (numpy arrays).
        NDVI = (NIR - Red) / (NIR + Red)
        """
        # Allow division by zero
        np.seterr(divide='ignore', invalid='ignore')
        
        # Calculate NDVI
        ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band.astype(float) + red_band.astype(float))
        
        # Handle nan/inf
        ndvi = np.nan_to_num(ndvi, nan=-1.0, posinf=1.0, neginf=-1.0)
        
        return ndvi
    
    @staticmethod
    def generate_heatmap(ndvi_matrix):
        """
        Convert NDVI matrix (-1 to 1) to a colored heatmap image (Red-Yellow-Green).
        Returns raw image bytes or saves to path.
        """
        # Normalize to 0-255
        norm_ndvi = ((ndvi_matrix + 1) / 2 * 255).astype(np.uint8)
        
        # Apply colormap (COLORMAP_JET or custom encoding)
        # Green is high NDVI, Red is low.
        # OpenCV Colormap: Jet goes Blue(low) to Red(high). 
        # We want Red(low) to Green(high).
        # Custom map or simple modification:
        
        # Let's use simple logic:
        # < 0.2: Red (Soil/Dead)
        # 0.2 - 0.5: Yellow (Unhealthy)
        # > 0.5: Green (Healthy)
        
        height, width = ndvi_matrix.shape
        heatmap = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Vectorized color assignment
        # Default Red
        heatmap[:,:] = [0, 0, 255] # BGR for OpenCV
        
        # Yellow for 0.1 to 0.4
        mask_yellow = (ndvi_matrix >= 0.1) & (ndvi_matrix < 0.4)
        heatmap[mask_yellow] = [0, 255, 255] # Cyan/Yellowish
        
        # Green for > 0.4
        mask_green = (ndvi_matrix >= 0.4)
        heatmap[mask_green] = [0, 255, 0]
        
        return heatmap

    @staticmethod
    def process_satellite_imagery(image_path, boundary_geojson):
        """
        Mock processing pipeline:
        1. Read image (assumed to contain Red/NIR channels)
        2. Clip to boundary
        3. Compute NDVI
        4. Return stats and path to heatmap
        """
        # In a real app, we would fetch Sentinel-2 data via API (e.g. SentinelHub or Google Earth Engine)
        # Here we simulate by generating a synthetic NDVI field
        
        # Parse GeoJSON (just for bounds usually) check bounds
        # geom = json.loads(boundary_geojson)
        
        # Synthetic Data Generation
        width, height = 500, 500
        
        # Create gradient NDVI
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x, y)
        synthetic_ndvi = 0.5 * np.sin(3*xv) + 0.5 * np.cos(3*yv) # Range approx -1 to 1
        
        # Generate Heatmap
        heatmap = SpatialUtils.generate_heatmap(synthetic_ndvi)
        
        # Calculate Stats
        stats = {
            "mean": float(np.mean(synthetic_ndvi)),
            "max": float(np.max(synthetic_ndvi)),
            "min": float(np.min(synthetic_ndvi)),
            "health_score": int((np.mean(synthetic_ndvi) + 1) * 50) # Scale 0-100
        }
        
        return heatmap, stats
