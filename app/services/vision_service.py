import logging
from typing import List, Dict, Any, Optional
from google.cloud import vision
from app.core.config import settings

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Vision API client"""
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS:
                self.client = vision.ImageAnnotatorClient()
                logger.info("Google Vision API client initialized successfully")
            else:
                logger.warning("Google Vision API credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision API client: {str(e)}")
            self.client = None
    
    async def detect_objects(self, image_url: str, cloudinary_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect objects in an image using Google Vision API
        
        Args:
            image_url: URL of the image to analyze
            cloudinary_id: Optional Cloudinary public ID
            
        Returns:
            Dict containing detected objects with bounding boxes
        """
        if not self.client:
            raise Exception("Google Vision API client not initialized")
        
        try:
            # Create image object from URL
            image = vision.Image()
            image.source.image_uri = image_url
            
            # Perform object localization
            response = self.client.object_localization(image=image)
            objects = response.localized_object_annotations
            
            # Process detected objects
            detected_objects = []
            for obj in objects:
                # Get bounding box coordinates
                vertices = obj.bounding_poly.normalized_vertices
                
                # Convert normalized coordinates to pixel coordinates
                # Note: We'll need image dimensions for this conversion
                # For now, we'll return normalized coordinates (0-1 range)
                min_x = min([vertex.x for vertex in vertices])
                min_y = min([vertex.y for vertex in vertices])
                max_x = max([vertex.x for vertex in vertices])
                max_y = max([vertex.y for vertex in vertices])
                
                detected_objects.append({
                    "name": obj.name,
                    "confidence": obj.score,
                    "bounding_box": {
                        "x": min_x,
                        "y": min_y,
                        "width": max_x - min_x,
                        "height": max_y - min_y,
                        "normalized": True  # Indicates coordinates are in 0-1 range
                    }
                })
            
            logger.info(f"Detected {len(detected_objects)} objects in image")
            
            return {
                "image_url": image_url,
                "cloudinary_id": cloudinary_id,
                "objects": detected_objects,
                "total_objects": len(detected_objects)
            }
            
        except Exception as e:
            logger.error(f"Error detecting objects: {str(e)}")
            raise Exception(f"Object detection failed: {str(e)}")
    
    async def detect_objects_with_dimensions(self, image_url: str, image_width: int, image_height: int, cloudinary_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect objects and return pixel coordinates based on image dimensions
        
        Args:
            image_url: URL of the image to analyze
            image_width: Width of the image in pixels
            image_height: Height of the image in pixels
            cloudinary_id: Optional Cloudinary public ID
            
        Returns:
            Dict containing detected objects with pixel-based bounding boxes
        """
        result = await self.detect_objects(image_url, cloudinary_id)
        
        # Convert normalized coordinates to pixel coordinates
        for obj in result["objects"]:
            bbox = obj["bounding_box"]
            if bbox["normalized"]:
                bbox.update({
                    "x": int(bbox["x"] * image_width),
                    "y": int(bbox["y"] * image_height),
                    "width": int(bbox["width"] * image_width),
                    "height": int(bbox["height"] * image_height),
                    "normalized": False
                })
        
        return result

# Global instance
vision_service = VisionService()