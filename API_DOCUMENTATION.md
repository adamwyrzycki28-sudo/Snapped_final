# Snapped AI API Documentation

## Overview

This document describes the enhanced FastAPI backend for Snapped AI with the following new features:

1. **Object Detection API** - Google Vision API integration for detecting objects in images
2. **Anonymous User System** - UUID-based user tracking without sign-up
3. **Search by Text API** - Text-based search functionality
4. **Admin Panel** - Comprehensive admin dashboard and management tools
5. **Ticket System** - Support ticket system with push notifications

## Base URL

```
http://localhost:12000/api/v1
```

## Authentication

The API uses anonymous user tracking. Users are automatically assigned a UUID when they first interact with the app.

## Core Endpoints

### 1. Object Detection API

**POST** `/images/detect-objects`

Detect objects in images using Google Vision API and return bounding boxes.

**Request:**
```bash
curl -X POST "http://localhost:12000/api/v1/images/detect-objects" \
  -F "image_url=https://example.com/image.jpg" \
  -F "cloudinary_id=abc123" \
  -F "point_x=100" \
  -F "point_y=150"
```

**Response:**
```json
{
  "objects": [
    {
      "name": "Shoe",
      "confidence": 0.95,
      "bounding_box": {
        "x": 50,
        "y": 75,
        "width": 200,
        "height": 150
      }
    }
  ],
  "image_url": "https://example.com/image.jpg",
  "cloudinary_id": "abc123",
  "point": {
    "x": 100,
    "y": 150
  }
}
```

### 2. Anonymous User Management

**POST** `/users/create`

Create a new anonymous user account.

**Request:**
```bash
curl -X POST "http://localhost:12000/api/v1/users/create" \
  -F "device_type=iOS" \
  -F "country=US"
```

**Response:**
```json
{
  "user_id": "d532bf13-e37c-44eb-ae10-2362bfb0f015",
  "device_type": "iOS",
  "country": "US",
  "first_seen": "2025-09-26T01:07:12.017900",
  "last_active": "2025-09-26T01:07:12.017908"
}
```

**GET** `/users/{user_id}`

Get user information and statistics.

**PUT** `/users/{user_id}/preferences`

Update user preferences.

### 3. Search by Text API

**POST** `/images/search-by-text`

Search for items using text queries. Automatically removes website names from titles (text after " | ").

**Request:**
```bash
curl -X POST "http://localhost:12000/api/v1/images/search-by-text" \
  -F "query=Nike Air Max shoes | Amazon" \
  -F "user_id=d532bf13-e37c-44eb-ae10-2362bfb0f015"
```

**Response:**
```json
{
  "search_id": 1,
  "search_time": "2025-09-26T01:07:37.426923",
  "image_path": "text_search:Nike Air Max shoes",
  "results": [
    {
      "id": 1,
      "title": "Nike Air Max 90",
      "link": "https://example.com/product",
      "image_url": "https://example.com/image.jpg",
      "price": "$120.00",
      "brand": "Nike",
      "source": "Amazon"
    }
  ],
  "total_results": 1
}
```

### 4. Enhanced Search API

The existing search API now includes `brand` as the source text retrieved from SerpAPI.

**Response includes:**
```json
{
  "results": [
    {
      "brand": "Nike",  // Now populated from SerpAPI source
      "source": "Amazon",
      "title": "Product Title",
      // ... other fields
    }
  ]
}
```

### 5. Click Tracking

**POST** `/users/{user_id}/clicks`

Record user click events for analytics.

**Request:**
```bash
curl -X POST "http://localhost:12000/api/v1/users/{user_id}/clicks" \
  -F "search_id=1" \
  -F "result_id=1" \
  -F "partner_domain=amazon.com" \
  -F "partner_name=Amazon" \
  -F "brand=Nike" \
  -F "item_title=Nike Air Max 90" \
  -F "price=$120.00" \
  -F "result_rank=1"
```

## Admin Panel Endpoints

### 1. Dashboard

**GET** `/admin/dashboard`

Get key metrics and trends for the admin dashboard.

**Response:**
```json
{
  "total_searches": 1250,
  "total_clicks": 340,
  "total_users": 890,
  "new_users": 45,
  "clicks_per_search": 0.27,
  "ctr": 27.2,
  "top_partners": [
    {"name": "Amazon", "clicks": 150, "ctr": 35.2},
    {"name": "eBay", "clicks": 90, "ctr": 28.1}
  ],
  "top_sources": [
    {"name": "Google Shopping", "searches": 500},
    {"name": "Amazon", "searches": 300}
  ],
  "seven_day_trend": [
    {"date": "2025-09-19", "searches": 45, "clicks": 12},
    {"date": "2025-09-20", "searches": 52, "clicks": 15}
  ],
  "thirty_day_trend": [
    {"week": "Week 1", "searches": 200, "clicks": 54},
    {"week": "Week 2", "searches": 250, "clicks": 68}
  ]
}
```

### 2. Searches Management

**GET** `/admin/searches`

Get paginated list of searches with filtering options.

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 50, max: 100)
- `start_date`: Filter by start date (YYYY-MM-DD)
- `end_date`: Filter by end date (YYYY-MM-DD)
- `user_id`: Filter by user ID
- `device_type`: Filter by device type
- `country`: Filter by country

**GET** `/admin/searches/{search_id}`

Get detailed information about a specific search including results and click timeline.

### 3. Clicks Management

**GET** `/admin/clicks`

Get paginated list of clicks with filtering options.

**Query Parameters:**
- `page`: Page number
- `per_page`: Results per page
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `partner`: Filter by partner
- `user_id`: Filter by user ID

### 4. Partners Analytics

**GET** `/admin/partners`

Get partner performance analytics.

**Response:**
```json
{
  "partners": [
    {
      "name": "Amazon",
      "clicks": 150,
      "searches_appeared": 400,
      "ctr": 37.5,
      "avg_position": 2.3
    }
  ]
}
```

### 5. Users Management

**GET** `/admin/users`

Get paginated list of users with behavior analytics.

**GET** `/admin/users/{user_id}`

Get detailed user information including search and click timeline.

### 6. Affiliate Links Management

**GET** `/admin/affiliate-links`

Get affiliate link configurations.

**POST** `/admin/affiliate-links`

Create or update affiliate link rules.

## Ticket System

### 1. Submit Ticket (User)

**POST** `/users/{user_id}/tickets`

Submit a support ticket when users can't find items.

**Request:**
```bash
curl -X POST "http://localhost:12000/api/v1/users/{user_id}/tickets" \
  -F "search_id=123" \
  -F "user_note=Can't find this specific model" \
  -F "crop_image_url=https://example.com/crop.jpg" \
  -F "original_image_url=https://example.com/original.jpg"
```

**Response:**
```json
{
  "id": 1,
  "user_id": "d532bf13-e37c-44eb-ae10-2362bfb0f015",
  "search_id": 123,
  "created_at": "2025-09-26T01:07:23.161727",
  "status": "open",
  "user_note": "Can't find this specific model",
  "crop_image_url": "https://example.com/crop.jpg"
}
```

### 2. Get User Tickets

**GET** `/users/{user_id}/tickets`

Get user's ticket history.

### 3. Admin Ticket Management

**GET** `/admin/tickets`

Get paginated list of tickets with filtering.

**Query Parameters:**
- `page`: Page number
- `per_page`: Results per page
- `status`: Filter by status (open, in-progress, resolved)
- `user_id`: Filter by user ID
- `start_date`: Filter by start date
- `end_date`: Filter by end date

**GET** `/admin/tickets/{ticket_id}`

Get detailed ticket information including search context and results.

**PUT** `/admin/tickets/{ticket_id}`

Update ticket status, add admin notes, and manual results.

**Request:**
```bash
curl -X PUT "http://localhost:12000/api/v1/admin/tickets/1" \
  -F "status=resolved" \
  -F "admin_notes=Found the item manually" \
  -F "manual_results=[{\"title\":\"Found Item\",\"link\":\"https://example.com\",\"price\":\"$99\"}]" \
  -F "resolved_by=admin123"
```

## Push Notifications

When an admin resolves a ticket, the system automatically sends a push notification to the user:

**Notification Content:**
- **Title:** "Item found!"
- **Body:** "One of our specialists sourced an item for you."
- **Data:** Contains ticket ID and user ID for deep linking

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

The API includes built-in rate limiting and request timing headers:
- `X-Process-Time`: Request processing time in seconds

## Database Schema

### Key Tables:
- `anonymous_users`: User tracking without authentication
- `image_searches`: Search history with user association
- `search_results`: Search results linked to searches
- `click_events`: Click tracking for analytics
- `tickets`: Support ticket system

### Indexes:
- Optimized indexes for date-based queries
- User-based filtering
- Search performance optimization

## Configuration

### Environment Variables:
- `GOOGLE_VISION_API_KEY`: Google Vision API credentials
- `FCM_SERVER_KEY`: Firebase Cloud Messaging key (for Android push notifications)
- `APNS_KEY_ID`: Apple Push Notification Service key ID (for iOS push notifications)
- `APNS_TEAM_ID`: Apple Developer Team ID

## Frontend Integration

### React Native Integration:
1. **Anonymous User Creation**: Call `/users/create` on app first launch
2. **Search Functionality**: Use both image and text search endpoints
3. **Click Tracking**: Record all user interactions
4. **Ticket Submission**: Add ticket form to search results page
5. **Push Notifications**: Handle incoming notifications for ticket resolution

### Example React Native Flow:
```javascript
// 1. Create anonymous user on app launch
const createUser = async () => {
  const response = await fetch('/api/v1/users/create', {
    method: 'POST',
    body: formData
  });
  const user = await response.json();
  // Store user_id locally
};

// 2. Submit ticket from search page
const submitTicket = async (userId, searchId, note, imageUrl) => {
  const formData = new FormData();
  formData.append('search_id', searchId);
  formData.append('user_note', note);
  formData.append('crop_image_url', imageUrl);
  
  const response = await fetch(`/api/v1/users/${userId}/tickets`, {
    method: 'POST',
    body: formData
  });
};

// 3. Handle push notifications
const handleNotification = (notification) => {
  if (notification.data.type === 'ticket_resolved') {
    // Navigate to ticket details or results
    navigateToTicket(notification.data.ticket_id);
  }
};
```

## Testing

The API includes comprehensive test coverage for all endpoints. Run tests with:

```bash
python -m pytest tests/
```

## Performance

- Database optimizations with proper indexing
- Connection pooling for external APIs
- Gzip compression for responses
- Request timing monitoring
- Efficient pagination for large datasets

## Security

- CORS configuration for cross-origin requests
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Input validation and sanitization
- SQL injection prevention through ORM
- Rate limiting and request monitoring