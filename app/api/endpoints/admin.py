from fastapi import APIRouter, Depends, HTTPException, Query, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.db.base import get_db
from app.models.schemas import (
    DashboardStatsResponse, AdminSearchesResponse, AdminSearchDetailsResponse,
    AdminClicksResponse, AdminPartnersResponse, AdminUsersResponse,
    TicketResponse, TicketUpdate
)
from app.services.admin_service import (
    get_dashboard_stats, get_searches_list, get_search_details, get_clicks_list
)
from app.services.ticket_service import (
    get_tickets_list, get_ticket_details, update_ticket
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard(
    days: int = Query(30, description="Number of days for trend analysis"),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Args:
        days: Number of days to look back for trends (default: 30)
        db: Database session
        
    Returns:
        DashboardStatsResponse with key metrics and trends
    """
    try:
        stats = await get_dashboard_stats(db, days)
        return DashboardStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

@router.get("/searches", response_model=AdminSearchesResponse)
async def get_searches(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of searches with filters
    
    Args:
        page: Page number (1-based)
        per_page: Results per page (max 100)
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        user_id: Filter by user ID
        device_type: Filter by device type
        country: Filter by country
        db: Database session
        
    Returns:
        AdminSearchesResponse with paginated search results
    """
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        result = await get_searches_list(
            db, page, per_page, parsed_start_date, parsed_end_date,
            user_id, device_type, country
        )
        
        return AdminSearchesResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting searches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting searches: {str(e)}")

@router.get("/searches/{search_id}", response_model=AdminSearchDetailsResponse)
async def get_search_detail(
    search_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific search
    
    Args:
        search_id: Search ID
        db: Database session
        
    Returns:
        AdminSearchDetailsResponse with search details, results, and clicks
    """
    try:
        details = await get_search_details(db, search_id)
        if not details:
            raise HTTPException(status_code=404, detail="Search not found")
        
        return AdminSearchDetailsResponse(**details)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting search details: {str(e)}")

@router.get("/clicks", response_model=AdminClicksResponse)
async def get_clicks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    partner_name: Optional[str] = Query(None, description="Filter by partner name"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    country: Optional[str] = Query(None, description="Filter by country"),
    group_by_user: bool = Query(False, description="Group results by user"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of clicks with filters
    
    Args:
        page: Page number (1-based)
        per_page: Results per page (max 100)
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        user_id: Filter by user ID
        partner_name: Filter by partner name
        device_type: Filter by device type
        country: Filter by country
        group_by_user: Group results by user
        db: Database session
        
    Returns:
        AdminClicksResponse with paginated click results
    """
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        result = await get_clicks_list(
            db, page, per_page, parsed_start_date, parsed_end_date,
            user_id, partner_name, device_type, country, group_by_user
        )
        
        return AdminClicksResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clicks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting clicks: {str(e)}")

@router.get("/partners")
async def get_partners(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get partner analytics
    
    Args:
        page: Page number (1-based)
        per_page: Results per page (max 100)
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        db: Database session
        
    Returns:
        Partner analytics data
    """
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # TODO: Implement get_partners_analytics in admin_service
        return {"message": "Partners endpoint - implementation pending"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting partners: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting partners: {str(e)}")

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """
    Get user analytics
    
    Args:
        page: Page number (1-based)
        per_page: Results per page (max 100)
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        device_type: Filter by device type
        country: Filter by country
        db: Database session
        
    Returns:
        User analytics data
    """
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        # TODO: Implement get_users_analytics in admin_service
        return {"message": "Users endpoint - implementation pending"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

@router.get("/tickets")
async def get_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get tickets for manual review
    
    Args:
        page: Page number (1-based)
        per_page: Results per page (max 100)
        status: Filter by status (open, in-progress, resolved)
        user_id: Filter by user ID
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        db: Database session
        
    Returns:
        Paginated list of tickets
    """
    try:
        # Parse dates
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        result = await get_tickets_list(
            db, page, per_page, status, user_id, parsed_start_date, parsed_end_date
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting tickets: {str(e)}")

@router.get("/tickets/{ticket_id}")
async def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific ticket
    
    Args:
        ticket_id: Ticket ID
        db: Database session
        
    Returns:
        Ticket details with search context
    """
    try:
        details = await get_ticket_details(db, ticket_id)
        if not details:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting ticket details: {str(e)}")

@router.put("/tickets/{ticket_id}")
async def update_ticket_endpoint(
    ticket_id: int,
    status: Optional[str] = Form(None),
    admin_notes: Optional[str] = Form(None),
    manual_results: Optional[str] = Form(None),
    resolved_by: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Update a ticket (add notes, change status, add manual results)
    
    Args:
        ticket_id: Ticket ID
        status: New status (open, in-progress, resolved)
        admin_notes: Admin notes
        manual_results: Manual search results (JSON string)
        resolved_by: Admin who resolved the ticket
        db: Database session
        
    Returns:
        Updated ticket information
    """
    try:
        ticket = await update_ticket(
            db, ticket_id, status, admin_notes, manual_results, resolved_by
        )
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
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
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")

@router.get("/affiliate-links")
async def get_affiliate_links(
    db: Session = Depends(get_db)
):
    """
    Get affiliate link management data
    
    Args:
        db: Database session
        
    Returns:
        Affiliate link configuration
    """
    try:
        # TODO: Implement affiliate links management
        return {"message": "Affiliate links endpoint - implementation pending"}
        
    except Exception as e:
        logger.error(f"Error getting affiliate links: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting affiliate links: {str(e)}")

@router.post("/affiliate-links")
async def create_affiliate_link(
    partner_name: str = Form(...),
    link_template: str = Form(...),
    is_default: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Create or update affiliate link configuration
    
    Args:
        partner_name: Partner name (e.g., Amazon, eBay)
        link_template: Link template with placeholders
        is_default: Whether this is the default rule
        db: Database session
        
    Returns:
        Created affiliate link configuration
    """
    try:
        # TODO: Implement affiliate link creation
        return {"message": "Create affiliate link endpoint - implementation pending"}
        
    except Exception as e:
        logger.error(f"Error creating affiliate link: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating affiliate link: {str(e)}")

@router.get("/export/{data_type}")
async def export_data(
    data_type: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Export data as CSV
    
    Args:
        data_type: Type of data to export (searches, clicks, partners, users, tickets)
        start_date: Filter by start date (YYYY-MM-DD format)
        end_date: Filter by end date (YYYY-MM-DD format)
        db: Database session
        
    Returns:
        CSV file download
    """
    try:
        if data_type not in ["searches", "clicks", "partners", "users", "tickets"]:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # TODO: Implement CSV export functionality
        return {"message": f"Export {data_type} endpoint - implementation pending"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")