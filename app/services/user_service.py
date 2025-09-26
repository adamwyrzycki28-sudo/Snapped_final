import logging
import uuid
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import AnonymousUser, ClickEvent, Ticket
from app.models.search import ImageSearch

logger = logging.getLogger(__name__)

async def create_anonymous_user(
    db: Session,
    device_type: Optional[str] = None,
    device_id: Optional[str] = None,
    country: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> AnonymousUser:
    """
    Create a new anonymous user
    
    Args:
        db: Database session
        device_type: Type of device (iOS, Android, Web)
        device_id: Device identifier
        country: Country code
        preferences: User preferences as dictionary
        
    Returns:
        AnonymousUser object
    """
    try:
        user = AnonymousUser(
            user_id=str(uuid.uuid4()),
            device_type=device_type,
            device_id=device_id,
            country=country,
            preferences=json.dumps(preferences) if preferences else None
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created anonymous user: {user.user_id}")
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating anonymous user: {str(e)}")
        raise

async def get_or_create_user(
    db: Session,
    user_id: Optional[str] = None,
    device_type: Optional[str] = None,
    device_id: Optional[str] = None,
    country: Optional[str] = None
) -> AnonymousUser:
    """
    Get existing user or create new one
    
    Args:
        db: Database session
        user_id: Existing user ID
        device_type: Type of device
        device_id: Device identifier
        country: Country code
        
    Returns:
        AnonymousUser object
    """
    try:
        user = None
        
        # Try to find existing user
        if user_id:
            user = db.query(AnonymousUser).filter(AnonymousUser.user_id == user_id).first()
            if user:
                # Update last active time
                user.last_active = datetime.utcnow()
                if device_type:
                    user.device_type = device_type
                if country:
                    user.country = country
                db.commit()
                logger.info(f"Found existing user: {user_id}")
                return user
        
        # Create new user if not found
        user = await create_anonymous_user(db, device_type, device_id, country)
        return user
        
    except Exception as e:
        logger.error(f"Error getting or creating user: {str(e)}")
        raise

async def update_user_preferences(
    db: Session,
    user_id: str,
    preferences: Dict[str, Any]
) -> Optional[AnonymousUser]:
    """
    Update user preferences
    
    Args:
        db: Database session
        user_id: User ID
        preferences: New preferences
        
    Returns:
        Updated AnonymousUser object or None if not found
    """
    try:
        user = db.query(AnonymousUser).filter(AnonymousUser.user_id == user_id).first()
        if not user:
            return None
        
        user.preferences = json.dumps(preferences)
        user.last_active = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"Updated preferences for user: {user_id}")
        return user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user preferences: {str(e)}")
        raise

async def record_click_event(
    db: Session,
    user_id: str,
    search_id: Optional[int] = None,
    result_id: Optional[int] = None,
    partner_domain: Optional[str] = None,
    partner_name: Optional[str] = None,
    brand: Optional[str] = None,
    item_title: Optional[str] = None,
    price: Optional[str] = None,
    result_rank: Optional[int] = None,
    original_url: Optional[str] = None,
    affiliate_url: Optional[str] = None,
    device_type: Optional[str] = None,
    country: Optional[str] = None
) -> ClickEvent:
    """
    Record a click event
    
    Args:
        db: Database session
        user_id: User ID
        search_id: Search ID
        result_id: Result ID
        partner_domain: Partner domain (e.g., amazon.com)
        partner_name: Partner name (e.g., Amazon)
        brand: Brand name
        item_title: Item title
        price: Price
        result_rank: Position in search results
        original_url: Original URL
        affiliate_url: Affiliate URL
        device_type: Device type
        country: Country code
        
    Returns:
        ClickEvent object
    """
    try:
        click_event = ClickEvent(
            user_id=user_id,
            search_id=search_id,
            result_id=result_id,
            partner_domain=partner_domain,
            partner_name=partner_name,
            brand=brand,
            item_title=item_title,
            price=price,
            result_rank=result_rank,
            original_url=original_url,
            affiliate_url=affiliate_url,
            device_type=device_type,
            country=country
        )
        
        db.add(click_event)
        db.commit()
        db.refresh(click_event)
        
        logger.info(f"Recorded click event for user: {user_id}")
        return click_event
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error recording click event: {str(e)}")
        raise

async def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Get user statistics
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with user statistics
    """
    try:
        user = db.query(AnonymousUser).filter(AnonymousUser.user_id == user_id).first()
        if not user:
            return {}
        
        # Get search count
        search_count = db.query(func.count(ImageSearch.id)).filter(
            ImageSearch.user_id == user_id
        ).scalar()
        
        # Get click count
        click_count = db.query(func.count(ClickEvent.id)).filter(
            ClickEvent.user_id == user_id
        ).scalar()
        
        # Calculate clicks per search
        clicks_per_search = click_count / search_count if search_count > 0 else 0
        
        # Get favorite partners (top 3)
        favorite_partners = db.query(
            ClickEvent.partner_name,
            func.count(ClickEvent.id).label('click_count')
        ).filter(
            ClickEvent.user_id == user_id,
            ClickEvent.partner_name.isnot(None)
        ).group_by(
            ClickEvent.partner_name
        ).order_by(
            func.count(ClickEvent.id).desc()
        ).limit(3).all()
        
        return {
            "user_id": user_id,
            "first_seen": user.first_seen,
            "last_active": user.last_active,
            "device_type": user.device_type,
            "country": user.country,
            "total_searches": search_count,
            "total_clicks": click_count,
            "clicks_per_search": round(clicks_per_search, 2),
            "favorite_partners": [
                {"name": partner[0], "clicks": partner[1]} 
                for partner in favorite_partners
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise