import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.models.user import Ticket, AnonymousUser
from app.models.search import ImageSearch
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

async def create_ticket(
    db: Session,
    user_id: str,
    search_id: Optional[int] = None,
    user_note: Optional[str] = None,
    crop_image_url: Optional[str] = None,
    original_image_url: Optional[str] = None
) -> Ticket:
    """
    Create a new support ticket
    
    Args:
        db: Database session
        user_id: User ID who submitted the ticket
        search_id: Related search ID (optional)
        user_note: User's note/description
        crop_image_url: URL of cropped image
        original_image_url: URL of original image
        
    Returns:
        Created Ticket object
    """
    try:
        ticket = Ticket(
            user_id=user_id,
            search_id=search_id,
            user_note=user_note,
            crop_image_url=crop_image_url,
            original_image_url=original_image_url,
            status="open"
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        logger.info(f"Created ticket {ticket.id} for user {user_id}")
        return ticket
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating ticket: {str(e)}")
        raise

async def get_tickets_list(
    db: Session,
    page: int = 1,
    per_page: int = 50,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get paginated list of tickets with filters
    
    Args:
        db: Database session
        page: Page number (1-based)
        per_page: Results per page
        status: Filter by status
        user_id: Filter by user ID
        start_date: Filter by start date
        end_date: Filter by end date
        
    Returns:
        Dictionary with tickets and pagination info
    """
    try:
        # Build query
        query = db.query(Ticket)
        
        # Apply filters
        if status:
            query = query.filter(Ticket.status == status)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if start_date:
            query = query.filter(Ticket.created_at >= start_date)
        if end_date:
            query = query.filter(Ticket.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        tickets = query.order_by(desc(Ticket.created_at)).offset(offset).limit(per_page).all()
        
        # Convert to dict format
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                "id": ticket.id,
                "user_id": ticket.user_id,
                "search_id": ticket.search_id,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
                "status": ticket.status,
                "user_note": ticket.user_note,
                "crop_image_url": ticket.crop_image_url,
                "original_image_url": ticket.original_image_url,
                "admin_notes": ticket.admin_notes,
                "manual_results": ticket.manual_results,
                "resolved_by": ticket.resolved_by,
                "resolved_at": ticket.resolved_at
            })
        
        return {
            "tickets": tickets_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Error getting tickets list: {str(e)}")
        raise

async def get_ticket_details(db: Session, ticket_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific ticket
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        
    Returns:
        Dictionary with ticket details and related search info
    """
    try:
        # Get ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {}
        
        # Get related search if exists
        search = None
        search_results = []
        if ticket.search_id:
            search = db.query(ImageSearch).filter(ImageSearch.id == ticket.search_id).first()
            if search:
                from app.models.search import SearchResult
                search_results = db.query(SearchResult).filter(
                    SearchResult.search_id == ticket.search_id
                ).all()
        
        return {
            "ticket": {
                "id": ticket.id,
                "user_id": ticket.user_id,
                "search_id": ticket.search_id,
                "created_at": ticket.created_at,
                "updated_at": ticket.updated_at,
                "status": ticket.status,
                "user_note": ticket.user_note,
                "crop_image_url": ticket.crop_image_url,
                "original_image_url": ticket.original_image_url,
                "admin_notes": ticket.admin_notes,
                "manual_results": ticket.manual_results,
                "resolved_by": ticket.resolved_by,
                "resolved_at": ticket.resolved_at
            },
            "search": {
                "id": search.id,
                "search_time": search.search_time,
                "image_path": search.image_path,
                "cloudinary_url": search.cloudinary_url,
                "device_type": search.device_type,
                "country": search.country
            } if search else None,
            "search_results": [
                {
                    "id": result.id,
                    "title": result.title,
                    "link": result.link,
                    "image_url": result.image_url,
                    "price": result.price,
                    "brand": result.brand,
                    "source": result.source
                }
                for result in search_results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting ticket details: {str(e)}")
        raise

async def update_ticket(
    db: Session,
    ticket_id: int,
    status: Optional[str] = None,
    admin_notes: Optional[str] = None,
    manual_results: Optional[str] = None,
    resolved_by: Optional[str] = None
) -> Optional[Ticket]:
    """
    Update a ticket
    
    Args:
        db: Database session
        ticket_id: Ticket ID
        status: New status
        admin_notes: Admin notes
        manual_results: Manual search results (JSON string)
        resolved_by: Admin who resolved the ticket
        
    Returns:
        Updated Ticket object or None if not found
    """
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        # Update fields
        if status is not None:
            old_status = ticket.status
            ticket.status = status
            if status == "resolved" and old_status != "resolved":
                ticket.resolved_at = datetime.utcnow()
                if resolved_by:
                    ticket.resolved_by = resolved_by
                
                # Send push notification when ticket is resolved
                try:
                    # Get user device info
                    user = db.query(AnonymousUser).filter(AnonymousUser.user_id == ticket.user_id).first()
                    if user:
                        await notification_service.send_ticket_resolved_notification(
                            user_id=ticket.user_id,
                            ticket_id=ticket.id,
                            device_token=getattr(user, 'device_token', None),
                            device_type=user.device_type
                        )
                except Exception as e:
                    logger.error(f"Error sending notification for resolved ticket {ticket.id}: {str(e)}")
        
        if admin_notes is not None:
            ticket.admin_notes = admin_notes
        
        if manual_results is not None:
            ticket.manual_results = manual_results
        
        ticket.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        logger.info(f"Updated ticket {ticket_id}")
        return ticket
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating ticket: {str(e)}")
        raise

async def get_user_tickets(
    db: Session,
    user_id: str,
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Get tickets for a specific user
    
    Args:
        db: Database session
        user_id: User ID
        page: Page number (1-based)
        per_page: Results per page
        
    Returns:
        Dictionary with user's tickets and pagination info
    """
    try:
        # Build query
        query = db.query(Ticket).filter(Ticket.user_id == user_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        tickets = query.order_by(desc(Ticket.created_at)).offset(offset).limit(per_page).all()
        
        # Convert to dict format
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                "id": ticket.id,
                "search_id": ticket.search_id,
                "created_at": ticket.created_at,
                "status": ticket.status,
                "user_note": ticket.user_note,
                "crop_image_url": ticket.crop_image_url,
                "original_image_url": ticket.original_image_url,
                "resolved_at": ticket.resolved_at
            })
        
        return {
            "tickets": tickets_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Error getting user tickets: {str(e)}")
        raise