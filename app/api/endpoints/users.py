from fastapi import APIRouter, Depends, HTTPException, Form, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
import json

from app.db.base import get_db
from app.models.schemas import (
    AnonymousUserCreate, AnonymousUserResponse, UserStatsResponse,
    ClickEventCreate, ClickEventResponse, TicketCreate, TicketResponse
)
from app.services.user_service import (
    create_anonymous_user, get_or_create_user, update_user_preferences,
    record_click_event, get_user_stats
)
from app.services.ticket_service import create_ticket, get_user_tickets

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=AnonymousUserResponse)
async def create_user(
    device_type: Optional[str] = Form(None),
    device_id: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    preferences: Optional[str] = Form(None),  # JSON string
    db: Session = Depends(get_db)
):
    """
    Create a new anonymous user
    
    Args:
        device_type: Type of device (iOS, Android, Web)
        device_id: Device identifier
        country: Country code
        preferences: User preferences as JSON string
        db: Database session
        
    Returns:
        AnonymousUserResponse with user details
    """
    try:
        # Parse preferences if provided
        parsed_preferences = None
        if preferences:
            try:
                parsed_preferences = json.loads(preferences)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid preferences JSON")
        
        user = await create_anonymous_user(
            db, device_type, device_id, country, parsed_preferences
        )
        
        return AnonymousUserResponse(
            user_id=user.user_id,
            device_type=user.device_type,
            country=user.country,
            first_seen=user.first_seen,
            last_active=user.last_active
        )
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.post("/get-or-create", response_model=AnonymousUserResponse)
async def get_or_create_user_endpoint(
    user_id: Optional[str] = Form(None),
    device_type: Optional[str] = Form(None),
    device_id: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Get existing user or create new one
    
    Args:
        user_id: Existing user ID (optional)
        device_type: Type of device
        device_id: Device identifier
        country: Country code
        db: Database session
        
    Returns:
        AnonymousUserResponse with user details
    """
    try:
        user = await get_or_create_user(db, user_id, device_type, device_id, country)
        
        return AnonymousUserResponse(
            user_id=user.user_id,
            device_type=user.device_type,
            country=user.country,
            first_seen=user.first_seen,
            last_active=user.last_active
        )
        
    except Exception as e:
        logger.error(f"Error getting or creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting or creating user: {str(e)}")

@router.put("/{user_id}/preferences", response_model=AnonymousUserResponse)
async def update_preferences(
    user_id: str,
    preferences: str = Form(...),  # JSON string
    db: Session = Depends(get_db)
):
    """
    Update user preferences
    
    Args:
        user_id: User ID
        preferences: New preferences as JSON string
        db: Database session
        
    Returns:
        Updated AnonymousUserResponse
    """
    try:
        # Parse preferences
        try:
            parsed_preferences = json.loads(preferences)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid preferences JSON")
        
        user = await update_user_preferences(db, user_id, parsed_preferences)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return AnonymousUserResponse(
            user_id=user.user_id,
            device_type=user.device_type,
            country=user.country,
            first_seen=user.first_seen,
            last_active=user.last_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")

@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user statistics
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UserStatsResponse with user statistics
    """
    try:
        stats = await get_user_stats(db, user_id)
        if not stats:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

@router.post("/{user_id}/clicks", response_model=ClickEventResponse)
async def record_click(
    user_id: str,
    search_id: Optional[int] = Form(None),
    result_id: Optional[int] = Form(None),
    partner_domain: Optional[str] = Form(None),
    partner_name: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    item_title: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    result_rank: Optional[int] = Form(None),
    original_url: Optional[str] = Form(None),
    affiliate_url: Optional[str] = Form(None),
    device_type: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Record a click event
    
    Args:
        user_id: User ID
        search_id: Search ID
        result_id: Result ID
        partner_domain: Partner domain
        partner_name: Partner name
        brand: Brand name
        item_title: Item title
        price: Price
        result_rank: Position in search results
        original_url: Original URL
        affiliate_url: Affiliate URL
        device_type: Device type
        country: Country code
        db: Database session
        
    Returns:
        ClickEventResponse with click details
    """
    try:
        click_event = await record_click_event(
            db, user_id, search_id, result_id, partner_domain, partner_name,
            brand, item_title, price, result_rank, original_url, affiliate_url,
            device_type, country
        )
        
        return ClickEventResponse(
            id=click_event.id,
            user_id=click_event.user_id,
            clicked_at=click_event.clicked_at,
            partner_domain=click_event.partner_domain,
            partner_name=click_event.partner_name,
            brand=click_event.brand,
            item_title=click_event.item_title,
            price=click_event.price,
            result_rank=click_event.result_rank
        )
        
    except Exception as e:
        logger.error(f"Error recording click: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error recording click: {str(e)}")

@router.post("/{user_id}/tickets", response_model=TicketResponse)
async def submit_ticket(
    user_id: str,
    search_id: Optional[int] = Form(None),
    user_note: Optional[str] = Form(None),
    crop_image_url: Optional[str] = Form(None),
    original_image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Submit a support ticket
    
    Args:
        user_id: User ID
        search_id: Related search ID (optional)
        user_note: User's note/description
        crop_image_url: URL of cropped image
        original_image_url: URL of original image
        db: Database session
        
    Returns:
        TicketResponse with ticket details
    """
    try:
        ticket = await create_ticket(
            db, user_id, search_id, user_note, crop_image_url, original_image_url
        )
        
        return TicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            search_id=ticket.search_id,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            status=ticket.status,
            user_note=ticket.user_note,
            crop_image_url=ticket.crop_image_url,
            original_image_url=ticket.original_image_url,
            admin_notes=ticket.admin_notes,
            resolved_by=ticket.resolved_by,
            resolved_at=ticket.resolved_at
        )
        
    except Exception as e:
        logger.error(f"Error submitting ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting ticket: {str(e)}")

@router.get("/{user_id}/tickets")
async def get_user_ticket_list(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=50, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Get user's tickets
    
    Args:
        user_id: User ID
        page: Page number (1-based)
        per_page: Results per page (max 50)
        db: Database session
        
    Returns:
        Paginated list of user's tickets
    """
    try:
        result = await get_user_tickets(db, user_id, page, per_page)
        return result
        
    except Exception as e:
        logger.error(f"Error getting user tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user tickets: {str(e)}")