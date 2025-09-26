import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from app.models.user import AnonymousUser, ClickEvent, Ticket
from app.models.search import ImageSearch, SearchResult

logger = logging.getLogger(__name__)

async def get_dashboard_stats(
    db: Session,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get dashboard statistics for the admin panel
    
    Args:
        db: Database session
        days: Number of days to look back for trends
        
    Returns:
        Dictionary with dashboard statistics
    """
    try:
        # Calculate date ranges
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        week_start = end_date - timedelta(days=7)
        
        # Total searches
        total_searches = db.query(func.count(ImageSearch.id)).scalar()
        
        # Total clicks
        total_clicks = db.query(func.count(ClickEvent.id)).scalar()
        
        # Total users
        total_users = db.query(func.count(AnonymousUser.user_id)).scalar()
        
        # New users in the period
        new_users = db.query(func.count(AnonymousUser.user_id)).filter(
            AnonymousUser.first_seen >= start_date
        ).scalar()
        
        # Searches in the period
        period_searches = db.query(func.count(ImageSearch.id)).filter(
            ImageSearch.search_time >= start_date
        ).scalar()
        
        # Clicks in the period
        period_clicks = db.query(func.count(ClickEvent.id)).filter(
            ClickEvent.clicked_at >= start_date
        ).scalar()
        
        # Calculate CTR (Click Through Rate)
        ctr = (period_clicks / period_searches * 100) if period_searches > 0 else 0
        
        # Clicks per search
        clicks_per_search = period_clicks / period_searches if period_searches > 0 else 0
        
        # Top partners
        top_partners = db.query(
            ClickEvent.partner_name,
            func.count(ClickEvent.id).label('clicks')
        ).filter(
            ClickEvent.clicked_at >= start_date,
            ClickEvent.partner_name.isnot(None)
        ).group_by(
            ClickEvent.partner_name
        ).order_by(
            desc('clicks')
        ).limit(10).all()
        
        # Top sources
        top_sources = db.query(
            SearchResult.source,
            func.count(SearchResult.id).label('results')
        ).join(
            ImageSearch, SearchResult.search_id == ImageSearch.id
        ).filter(
            ImageSearch.search_time >= start_date,
            SearchResult.source.isnot(None)
        ).group_by(
            SearchResult.source
        ).order_by(
            desc('results')
        ).limit(10).all()
        
        # 7-day trend data
        seven_day_trend = []
        for i in range(7):
            day_start = end_date - timedelta(days=i+1)
            day_end = end_date - timedelta(days=i)
            
            day_searches = db.query(func.count(ImageSearch.id)).filter(
                and_(
                    ImageSearch.search_time >= day_start,
                    ImageSearch.search_time < day_end
                )
            ).scalar()
            
            day_clicks = db.query(func.count(ClickEvent.id)).filter(
                and_(
                    ClickEvent.clicked_at >= day_start,
                    ClickEvent.clicked_at < day_end
                )
            ).scalar()
            
            seven_day_trend.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "searches": day_searches,
                "clicks": day_clicks
            })
        
        # 30-day trend data (weekly aggregation)
        thirty_day_trend = []
        for i in range(4):
            week_start_date = end_date - timedelta(weeks=i+1)
            week_end_date = end_date - timedelta(weeks=i)
            
            week_searches = db.query(func.count(ImageSearch.id)).filter(
                and_(
                    ImageSearch.search_time >= week_start_date,
                    ImageSearch.search_time < week_end_date
                )
            ).scalar()
            
            week_clicks = db.query(func.count(ClickEvent.id)).filter(
                and_(
                    ClickEvent.clicked_at >= week_start_date,
                    ClickEvent.clicked_at < week_end_date
                )
            ).scalar()
            
            thirty_day_trend.append({
                "week": f"Week {4-i}",
                "searches": week_searches,
                "clicks": week_clicks
            })
        
        return {
            "total_searches": total_searches,
            "total_clicks": total_clicks,
            "total_users": total_users,
            "new_users": new_users,
            "clicks_per_search": round(clicks_per_search, 2),
            "ctr": round(ctr, 2),
            "top_partners": [
                {"name": partner[0], "clicks": partner[1]} 
                for partner in top_partners
            ],
            "top_sources": [
                {"name": source[0], "results": source[1]} 
                for source in top_sources
            ],
            "seven_day_trend": list(reversed(seven_day_trend)),
            "thirty_day_trend": list(reversed(thirty_day_trend))
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise

async def get_searches_list(
    db: Session,
    page: int = 1,
    per_page: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[str] = None,
    device_type: Optional[str] = None,
    country: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get paginated list of searches with filters
    
    Args:
        db: Database session
        page: Page number (1-based)
        per_page: Results per page
        start_date: Filter by start date
        end_date: Filter by end date
        user_id: Filter by user ID
        device_type: Filter by device type
        country: Filter by country
        
    Returns:
        Dictionary with searches and pagination info
    """
    try:
        # Build query
        query = db.query(ImageSearch).join(
            AnonymousUser, ImageSearch.user_id == AnonymousUser.user_id, isouter=True
        )
        
        # Apply filters
        if start_date:
            query = query.filter(ImageSearch.search_time >= start_date)
        if end_date:
            query = query.filter(ImageSearch.search_time <= end_date)
        if user_id:
            query = query.filter(ImageSearch.user_id == user_id)
        if device_type:
            query = query.filter(ImageSearch.device_type == device_type)
        if country:
            query = query.filter(ImageSearch.country == country)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        searches = query.order_by(desc(ImageSearch.search_time)).offset(offset).limit(per_page).all()
        
        # Get result counts and click counts for each search
        search_data = []
        for search in searches:
            result_count = db.query(func.count(SearchResult.id)).filter(
                SearchResult.search_id == search.id
            ).scalar()
            
            click_count = db.query(func.count(ClickEvent.id)).filter(
                ClickEvent.search_id == search.id
            ).scalar()
            
            search_data.append({
                "id": search.id,
                "user_id": search.user_id,
                "search_time": search.search_time,
                "image_path": search.image_path,
                "device_type": search.device_type,
                "country": search.country,
                "is_clipped": search.is_clipped,
                "cloudinary_url": search.cloudinary_url,
                "result_count": result_count,
                "click_count": click_count
            })
        
        return {
            "searches": search_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Error getting searches list: {str(e)}")
        raise

async def get_search_details(db: Session, search_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific search
    
    Args:
        db: Database session
        search_id: Search ID
        
    Returns:
        Dictionary with search details
    """
    try:
        # Get search
        search = db.query(ImageSearch).filter(ImageSearch.id == search_id).first()
        if not search:
            return {}
        
        # Get results
        results = db.query(SearchResult).filter(
            SearchResult.search_id == search_id
        ).order_by(SearchResult.id).all()
        
        # Get clicks for this search
        clicks = db.query(ClickEvent).filter(
            ClickEvent.search_id == search_id
        ).order_by(ClickEvent.clicked_at).all()
        
        # Get user info
        user = db.query(AnonymousUser).filter(
            AnonymousUser.user_id == search.user_id
        ).first() if search.user_id else None
        
        return {
            "search": {
                "id": search.id,
                "user_id": search.user_id,
                "search_time": search.search_time,
                "image_path": search.image_path,
                "original_image_path": search.original_image_path,
                "is_clipped": search.is_clipped,
                "cloudinary_url": search.cloudinary_url,
                "original_cloudinary_url": search.original_cloudinary_url,
                "device_type": search.device_type,
                "country": search.country
            },
            "user": {
                "user_id": user.user_id,
                "device_type": user.device_type,
                "country": user.country,
                "first_seen": user.first_seen,
                "last_active": user.last_active
            } if user else None,
            "results": [
                {
                    "id": result.id,
                    "title": result.title,
                    "link": result.link,
                    "image_url": result.image_url,
                    "price": result.price,
                    "brand": result.brand,
                    "source": result.source,
                    "rating": result.rating,
                    "reviews_count": result.reviews_count
                }
                for result in results
            ],
            "clicks": [
                {
                    "id": click.id,
                    "clicked_at": click.clicked_at,
                    "result_id": click.result_id,
                    "partner_name": click.partner_name,
                    "partner_domain": click.partner_domain,
                    "brand": click.brand,
                    "item_title": click.item_title,
                    "price": click.price,
                    "result_rank": click.result_rank
                }
                for click in clicks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting search details: {str(e)}")
        raise

async def get_clicks_list(
    db: Session,
    page: int = 1,
    per_page: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[str] = None,
    partner_name: Optional[str] = None,
    device_type: Optional[str] = None,
    country: Optional[str] = None,
    group_by_user: bool = False
) -> Dict[str, Any]:
    """
    Get paginated list of clicks with filters
    
    Args:
        db: Database session
        page: Page number (1-based)
        per_page: Results per page
        start_date: Filter by start date
        end_date: Filter by end date
        user_id: Filter by user ID
        partner_name: Filter by partner name
        device_type: Filter by device type
        country: Filter by country
        group_by_user: Group results by user
        
    Returns:
        Dictionary with clicks and pagination info
    """
    try:
        if group_by_user:
            # Group by user
            query = db.query(
                ClickEvent.user_id,
                func.count(ClickEvent.id).label('total_clicks'),
                func.count(func.distinct(ClickEvent.search_id)).label('searches_with_clicks'),
                func.max(ClickEvent.clicked_at).label('last_click')
            ).join(
                AnonymousUser, ClickEvent.user_id == AnonymousUser.user_id, isouter=True
            )
            
            # Apply filters
            if start_date:
                query = query.filter(ClickEvent.clicked_at >= start_date)
            if end_date:
                query = query.filter(ClickEvent.clicked_at <= end_date)
            if user_id:
                query = query.filter(ClickEvent.user_id == user_id)
            if partner_name:
                query = query.filter(ClickEvent.partner_name == partner_name)
            if device_type:
                query = query.filter(ClickEvent.device_type == device_type)
            if country:
                query = query.filter(ClickEvent.country == country)
            
            query = query.group_by(ClickEvent.user_id)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            results = query.order_by(desc('last_click')).offset(offset).limit(per_page).all()
            
            clicks_data = [
                {
                    "user_id": result.user_id,
                    "total_clicks": result.total_clicks,
                    "searches_with_clicks": result.searches_with_clicks,
                    "last_click": result.last_click
                }
                for result in results
            ]
            
        else:
            # Individual clicks
            query = db.query(ClickEvent).join(
                AnonymousUser, ClickEvent.user_id == AnonymousUser.user_id, isouter=True
            )
            
            # Apply filters
            if start_date:
                query = query.filter(ClickEvent.clicked_at >= start_date)
            if end_date:
                query = query.filter(ClickEvent.clicked_at <= end_date)
            if user_id:
                query = query.filter(ClickEvent.user_id == user_id)
            if partner_name:
                query = query.filter(ClickEvent.partner_name == partner_name)
            if device_type:
                query = query.filter(ClickEvent.device_type == device_type)
            if country:
                query = query.filter(ClickEvent.country == country)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            clicks = query.order_by(desc(ClickEvent.clicked_at)).offset(offset).limit(per_page).all()
            
            clicks_data = [
                {
                    "id": click.id,
                    "user_id": click.user_id,
                    "search_id": click.search_id,
                    "clicked_at": click.clicked_at,
                    "partner_name": click.partner_name,
                    "partner_domain": click.partner_domain,
                    "brand": click.brand,
                    "item_title": click.item_title,
                    "price": click.price,
                    "result_rank": click.result_rank,
                    "original_url": click.original_url,
                    "affiliate_url": click.affiliate_url,
                    "device_type": click.device_type,
                    "country": click.country
                }
                for click in clicks
            ]
        
        return {
            "clicks": clicks_data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "grouped_by_user": group_by_user
        }
        
    except Exception as e:
        logger.error(f"Error getting clicks list: {str(e)}")
        raise