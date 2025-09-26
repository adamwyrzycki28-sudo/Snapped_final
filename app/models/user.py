from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class AnonymousUser(Base):
    __tablename__ = "anonymous_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    device_type = Column(String, nullable=True)  # iOS, Android, Web
    device_id = Column(String, nullable=True)  # Device identifier
    country = Column(String, nullable=True)  # Country code
    first_seen = Column(DateTime, default=datetime.utcnow, index=True)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True)
    
    # Preferences stored as JSON string
    preferences = Column(Text, nullable=True)
    
    # Relationships
    searches = relationship("ImageSearch", back_populates="user", cascade="all, delete-orphan")
    clicks = relationship("ClickEvent", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    
    # Create indexes for faster queries
    __table_args__ = (
        Index('ix_anonymous_users_last_active_desc', last_active.desc()),
        Index('ix_anonymous_users_device_country', device_type, country),
    )

class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("anonymous_users.user_id"), nullable=False, index=True)
    search_id = Column(Integer, ForeignKey("image_searches.id"), nullable=True, index=True)  # Reference to ImageSearch
    result_id = Column(Integer, ForeignKey("search_results.id"), nullable=True, index=True)  # Reference to SearchResult
    
    # Click details
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)
    partner_domain = Column(String, nullable=True, index=True)  # amazon.com, ebay.com, etc.
    partner_name = Column(String, nullable=True, index=True)  # Amazon, eBay, etc.
    brand = Column(String, nullable=True, index=True)
    item_title = Column(String, nullable=True)
    price = Column(String, nullable=True)
    result_rank = Column(Integer, nullable=True)  # Position in search results
    
    # URL details
    original_url = Column(String, nullable=True)
    affiliate_url = Column(String, nullable=True)
    
    # Device and location
    device_type = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Relationship
    user = relationship("AnonymousUser", back_populates="clicks")
    
    # Create indexes for faster queries
    __table_args__ = (
        Index('ix_click_events_clicked_at_desc', clicked_at.desc()),
        Index('ix_click_events_partner_brand', partner_domain, brand),
        Index('ix_click_events_user_clicked_at', user_id, clicked_at.desc()),
    )

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("anonymous_users.user_id"), nullable=False, index=True)
    search_id = Column(Integer, ForeignKey("image_searches.id"), nullable=True, index=True)  # Reference to ImageSearch
    
    # Ticket details
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="open", index=True)  # open, in_progress, resolved, closed
    
    # User submission
    user_note = Column(Text, nullable=True)
    crop_image_url = Column(String, nullable=True)  # URL to the cropped image
    original_image_url = Column(String, nullable=True)  # URL to the original image
    
    # Admin response
    admin_notes = Column(Text, nullable=True)
    resolved_by = Column(String, nullable=True)  # Admin user ID
    resolved_at = Column(DateTime, nullable=True)
    
    # Manual results added by admin
    manual_results = Column(Text, nullable=True)  # JSON string of manual results
    
    # Relationship
    user = relationship("AnonymousUser", back_populates="tickets")
    
    # Create indexes for faster queries
    __table_args__ = (
        Index('ix_tickets_created_at_desc', created_at.desc()),
        Index('ix_tickets_status_created_at', status, created_at.desc()),
        Index('ix_tickets_user_created_at', user_id, created_at.desc()),
    )