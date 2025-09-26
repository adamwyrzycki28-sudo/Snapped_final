from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# Search Result Schema
class SearchResultBase(BaseModel):
    title: Optional[str] = None
    link: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[str] = None
    brand: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None

class SearchResultCreate(SearchResultBase):
    raw_data: Optional[str] = None

class SearchResult(SearchResultBase):
    id: int
    search_id: int
    
    class Config:
        orm_mode = True
        from_attributes = True

# Image Search Schema
class ImageSearchBase(BaseModel):
    image_path: str
    original_image_path: Optional[str] = None
    is_clipped: bool = False
    cloudinary_public_id: Optional[str] = None
    cloudinary_url: Optional[str] = None
    original_cloudinary_public_id: Optional[str] = None
    original_cloudinary_url: Optional[str] = None

class ImageSearchCreate(ImageSearchBase):
    pass

class ImageSearch(ImageSearchBase):
    id: int
    search_time: datetime
    results: List[SearchResult] = []
    
    class Config:
        orm_mode = True
        from_attributes = True

# Request Schemas
class ImageClipRequest(BaseModel):
    image_path: str
    x: int
    y: int
    width: int
    height: int

# Response Schemas
class ImageUploadResponse(BaseModel):
    image_path: str
    cloudinary_public_id: Optional[str] = None
    cloudinary_url: Optional[str] = None
    message: str = "Image uploaded successfully"

class ImageClipResponse(BaseModel):
    image_path: str
    original_image_path: str
    cloudinary_public_id: Optional[str] = None
    cloudinary_url: Optional[str] = None
    original_cloudinary_public_id: Optional[str] = None
    original_cloudinary_url: Optional[str] = None
    message: str = "Image clipped successfully"

class SimilarProductsResponse(BaseModel):
    search_id: int
    search_time: datetime
    image_path: str
    original_image_path: Optional[str] = None
    is_clipped: bool
    cloudinary_public_id: Optional[str] = None
    cloudinary_url: Optional[str] = None
    original_cloudinary_public_id: Optional[str] = None
    original_cloudinary_url: Optional[str] = None
    results: List[SearchResult]
    total_results: int

# API Schemas for all searches
class SearchListResponse(BaseModel):
    searches: List[ImageSearch]
    total: int
    page: int
    page_size: int

# Filter schemas
class ProductFilter(BaseModel):
    brand: Optional[List[str]] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    source: Optional[List[str]] = None

# Object Detection Schemas
class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    normalized: bool = False

class DetectedObject(BaseModel):
    name: str
    confidence: float
    bounding_box: BoundingBox

class ObjectDetectionRequest(BaseModel):
    image_url: str
    cloudinary_id: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None

class ObjectDetectionResponse(BaseModel):
    image_url: str
    cloudinary_id: Optional[str] = None
    objects: List[DetectedObject]
    total_objects: int

# User Schemas
class AnonymousUserCreate(BaseModel):
    device_type: Optional[str] = None
    device_id: Optional[str] = None
    country: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class AnonymousUserResponse(BaseModel):
    user_id: str
    device_type: Optional[str] = None
    country: Optional[str] = None
    first_seen: datetime
    last_active: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True

class UserStatsResponse(BaseModel):
    user_id: str
    first_seen: datetime
    last_active: datetime
    device_type: Optional[str] = None
    country: Optional[str] = None
    total_searches: int
    total_clicks: int
    clicks_per_search: float
    favorite_partners: List[Dict[str, Any]]

# Click Event Schemas
class ClickEventCreate(BaseModel):
    search_id: Optional[int] = None
    result_id: Optional[int] = None
    partner_domain: Optional[str] = None
    partner_name: Optional[str] = None
    brand: Optional[str] = None
    item_title: Optional[str] = None
    price: Optional[str] = None
    result_rank: Optional[int] = None
    original_url: Optional[str] = None
    affiliate_url: Optional[str] = None

class ClickEventResponse(BaseModel):
    id: int
    user_id: str
    clicked_at: datetime
    partner_domain: Optional[str] = None
    partner_name: Optional[str] = None
    brand: Optional[str] = None
    item_title: Optional[str] = None
    price: Optional[str] = None
    result_rank: Optional[int] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

# Ticket Schemas
class TicketCreate(BaseModel):
    search_id: Optional[int] = None
    user_note: Optional[str] = None
    crop_image_url: Optional[str] = None
    original_image_url: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    user_id: str
    search_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    status: str
    user_note: Optional[str] = None
    crop_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    admin_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    manual_results: Optional[str] = None

# Admin Panel Schemas
class DashboardStatsResponse(BaseModel):
    total_searches: int
    total_clicks: int
    total_users: int
    new_users: int
    clicks_per_search: float
    ctr: float
    top_partners: List[Dict[str, Any]]
    top_sources: List[Dict[str, Any]]
    seven_day_trend: List[Dict[str, Any]]
    thirty_day_trend: List[Dict[str, Any]]

class AdminSearchItem(BaseModel):
    id: int
    user_id: Optional[str]
    search_time: datetime
    image_path: str
    device_type: Optional[str]
    country: Optional[str]
    is_clipped: bool
    cloudinary_url: Optional[str]
    result_count: int
    click_count: int

class AdminSearchesResponse(BaseModel):
    searches: List[AdminSearchItem]
    total: int
    page: int
    per_page: int
    total_pages: int

class AdminSearchDetailsResponse(BaseModel):
    search: Dict[str, Any]
    user: Optional[Dict[str, Any]]
    results: List[Dict[str, Any]]
    clicks: List[Dict[str, Any]]

class AdminClickItem(BaseModel):
    id: int
    user_id: str
    search_id: Optional[int]
    clicked_at: datetime
    partner_name: Optional[str]
    partner_domain: Optional[str]
    brand: Optional[str]
    item_title: Optional[str]
    price: Optional[str]
    result_rank: Optional[int]
    original_url: Optional[str]
    affiliate_url: Optional[str]
    device_type: Optional[str]
    country: Optional[str]

class AdminClicksResponse(BaseModel):
    clicks: List[Dict[str, Any]]  # Can be AdminClickItem or grouped data
    total: int
    page: int
    per_page: int
    total_pages: int
    grouped_by_user: bool

class AdminPartnerStats(BaseModel):
    partner_name: str
    clicks: int
    searches_appeared: int
    ctr_percentage: float
    average_position: float

class AdminPartnersResponse(BaseModel):
    partners: List[AdminPartnerStats]
    total: int
    page: int
    per_page: int
    total_pages: int

class AdminUserItem(BaseModel):
    user_id: str
    device_type: Optional[str]
    country: Optional[str]
    first_seen: datetime
    last_active: datetime
    total_searches: int
    total_clicks: int
    avg_clicks_per_search: float
    favorite_partners: List[Dict[str, Any]]

class AdminUsersResponse(BaseModel):
    users: List[AdminUserItem]
    total: int
    page: int
    per_page: int
    total_pages: int