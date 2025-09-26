# Snapped AI - Enhanced FastAPI Backend

A comprehensive FastAPI backend for AI-powered product discovery with advanced features including object detection, anonymous user tracking, admin analytics, and support ticket system.

## 🚀 Features

### Core Search Functionality
- **Image Upload & Processing**: Upload and clip images with Cloudinary integration
- **Visual Search**: Find similar products using Google Reverse Image Search via SerpAPI
- **Object Detection**: Google Vision API integration for precise object detection with bounding boxes
- **Text Search**: Search products by text with automatic title cleaning
- **Smart Filtering**: Advanced duplicate filtering and result optimization

### User Experience
- **Anonymous User System**: Instant app usage without sign-up requirements
- **UUID-based Tracking**: Secure user tracking with device and location data
- **Search History**: Complete search and interaction history
- **Support Tickets**: User-friendly ticket submission for difficult searches
- **Push Notifications**: Real-time notifications for ticket resolution

### Admin & Analytics
- **Comprehensive Dashboard**: Real-time metrics, trends, and performance analytics
- **User Management**: Anonymous user behavior tracking and analytics
- **Search Analytics**: Detailed search performance and result quality metrics
- **Click Tracking**: Partner performance and user engagement analytics
- **Ticket Management**: Complete support ticket lifecycle management
- **Affiliate Management**: Partner link management and revenue optimization

### Technical Features
- **High Performance**: Async/await throughout, connection pooling, caching
- **Scalable Architecture**: Optimized database indexes, pagination, monitoring
- **Security**: Input validation, CORS, rate limiting, security headers
- **Mobile-Ready**: React Native integration with push notification support

## 📋 API Endpoints

### 🔍 Search & Detection
- `POST /api/v1/images/upload` - Upload an image
- `POST /api/v1/images/clip` - Clip an uploaded image
- `POST /api/v1/images/search` - Visual search using uploaded image
- `POST /api/v1/images/search-by-text` - Text-based product search
- `POST /api/v1/images/detect-objects` - Object detection with bounding boxes
- `GET /api/v1/images/searches/{search_id}` - Get specific search results
- `GET /api/v1/images/searches` - Get recent search history

### 👤 User Management
- `POST /api/v1/users/create` - Create anonymous user account
- `GET /api/v1/users/{user_id}` - Get user information and statistics
- `PUT /api/v1/users/{user_id}/preferences` - Update user preferences
- `POST /api/v1/users/{user_id}/clicks` - Record click events for analytics

### 🎫 Support Tickets
- `POST /api/v1/users/{user_id}/tickets` - Submit support ticket
- `GET /api/v1/users/{user_id}/tickets` - Get user's ticket history

### 🛠️ Admin Panel
- `GET /api/v1/admin/dashboard` - Dashboard with key metrics and trends
- `GET /api/v1/admin/searches` - Search management with filtering
- `GET /api/v1/admin/clicks` - Click analytics and tracking
- `GET /api/v1/admin/partners` - Partner performance analytics
- `GET /api/v1/admin/users` - User behavior and analytics
- `GET /api/v1/admin/tickets` - Ticket management system
- `PUT /api/v1/admin/tickets/{ticket_id}` - Update ticket status and resolution
- `GET /api/v1/admin/affiliate-links` - Affiliate link management

## 🛠️ Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/adamwyrzycki28-sudo/Snapped_final.git
   cd Snapped_final
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Unix (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory with the following configuration:
   ```env
   # Core API Configuration
   SERPAPI_API_KEY=your_serpapi_api_key
   DATABASE_URL=sqlite:///./app.db
   MAX_SIMILAR_PRODUCTS=30
   HOST=0.0.0.0
   PORT=12000
   
   # Google Vision API (for object detection)
   GOOGLE_VISION_API_KEY=your_google_vision_api_key
   
   # Cloudinary settings (optional)
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   USE_CLOUDINARY=false
   
   # Push Notifications (optional)
   FCM_SERVER_KEY=your_fcm_server_key
   APNS_KEY_ID=your_apns_key_id
   APNS_TEAM_ID=your_apns_team_id
   ```

5. **Initialize the database:**
   ```bash
   python -c "from app.db.init_db import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```

For more detailed setup instructions, see [SETUP.md](SETUP.md).

## 📱 React Native Integration

### Quick Start Integration

1. **Install Required Dependencies:**
   ```bash
   npm install @react-native-async-storage/async-storage
   npm install @react-native-community/push-notification-ios
   npm install react-native-push-notification
   npm install react-native-image-picker
   ```

2. **Create API Service:**
   ```javascript
   // services/api.js
   const API_BASE_URL = 'http://your-backend-url.com/api/v1';
   
   class SnappedAPI {
     constructor() {
       this.userId = null;
     }
   
     // Initialize anonymous user on app launch
     async initializeUser(deviceType, country) {
       try {
         const formData = new FormData();
         formData.append('device_type', deviceType);
         formData.append('country', country);
   
         const response = await fetch(`${API_BASE_URL}/users/create`, {
           method: 'POST',
           body: formData,
         });
   
         const user = await response.json();
         this.userId = user.user_id;
         
         // Store user ID locally
         await AsyncStorage.setItem('snapped_user_id', user.user_id);
         return user;
       } catch (error) {
         console.error('Error creating user:', error);
         throw error;
       }
     }
   
     // Load existing user ID
     async loadUserId() {
       try {
         const userId = await AsyncStorage.getItem('snapped_user_id');
         if (userId) {
           this.userId = userId;
         }
         return userId;
       } catch (error) {
         console.error('Error loading user ID:', error);
         return null;
       }
     }
   
     // Visual search with image
     async searchByImage(imageUri, isClipped = false) {
       try {
         const formData = new FormData();
         formData.append('image', {
           uri: imageUri,
           type: 'image/jpeg',
           name: 'search_image.jpg',
         });
         formData.append('user_id', this.userId);
         formData.append('is_clipped', isClipped.toString());
   
         const response = await fetch(`${API_BASE_URL}/images/search`, {
           method: 'POST',
           body: formData,
         });
   
         return await response.json();
       } catch (error) {
         console.error('Error searching by image:', error);
         throw error;
       }
     }
   
     // Text-based search
     async searchByText(query) {
       try {
         const formData = new FormData();
         formData.append('query', query);
         formData.append('user_id', this.userId);
   
         const response = await fetch(`${API_BASE_URL}/images/search-by-text`, {
           method: 'POST',
           body: formData,
         });
   
         return await response.json();
       } catch (error) {
         console.error('Error searching by text:', error);
         throw error;
       }
     }
   
     // Object detection
     async detectObjects(imageUrl, cloudinaryId, pointX, pointY) {
       try {
         const formData = new FormData();
         formData.append('image_url', imageUrl);
         formData.append('cloudinary_id', cloudinaryId);
         if (pointX !== undefined) formData.append('point_x', pointX.toString());
         if (pointY !== undefined) formData.append('point_y', pointY.toString());
   
         const response = await fetch(`${API_BASE_URL}/images/detect-objects`, {
           method: 'POST',
           body: formData,
         });
   
         return await response.json();
       } catch (error) {
         console.error('Error detecting objects:', error);
         throw error;
       }
     }
   
     // Submit support ticket
     async submitTicket(searchId, userNote, cropImageUrl, originalImageUrl) {
       try {
         const formData = new FormData();
         if (searchId) formData.append('search_id', searchId.toString());
         formData.append('user_note', userNote);
         formData.append('crop_image_url', cropImageUrl);
         if (originalImageUrl) formData.append('original_image_url', originalImageUrl);
   
         const response = await fetch(`${API_BASE_URL}/users/${this.userId}/tickets`, {
           method: 'POST',
           body: formData,
         });
   
         return await response.json();
       } catch (error) {
         console.error('Error submitting ticket:', error);
         throw error;
       }
     }
   
     // Record click event
     async recordClick(searchId, resultId, partnerDomain, partnerName, brand, itemTitle, price, resultRank) {
       try {
         const formData = new FormData();
         formData.append('search_id', searchId.toString());
         formData.append('result_id', resultId.toString());
         formData.append('partner_domain', partnerDomain);
         formData.append('partner_name', partnerName);
         if (brand) formData.append('brand', brand);
         formData.append('item_title', itemTitle);
         if (price) formData.append('price', price);
         formData.append('result_rank', resultRank.toString());
   
         const response = await fetch(`${API_BASE_URL}/users/${this.userId}/clicks`, {
           method: 'POST',
           body: formData,
         });
   
         return await response.json();
       } catch (error) {
         console.error('Error recording click:', error);
         throw error;
       }
     }
   
     // Get user tickets
     async getUserTickets() {
       try {
         const response = await fetch(`${API_BASE_URL}/users/${this.userId}/tickets`);
         return await response.json();
       } catch (error) {
         console.error('Error getting user tickets:', error);
         throw error;
       }
     }
   }
   
   export default new SnappedAPI();
   ```

3. **App Initialization:**
   ```javascript
   // App.js
   import React, { useEffect } from 'react';
   import { Platform } from 'react-native';
   import AsyncStorage from '@react-native-async-storage/async-storage';
   import PushNotification from 'react-native-push-notification';
   import SnappedAPI from './services/api';
   
   const App = () => {
     useEffect(() => {
       initializeApp();
       setupPushNotifications();
     }, []);
   
     const initializeApp = async () => {
       try {
         // Try to load existing user ID
         const existingUserId = await SnappedAPI.loadUserId();
         
         if (!existingUserId) {
           // Create new anonymous user
           const deviceType = Platform.OS === 'ios' ? 'iOS' : 'Android';
           const country = 'US'; // You can get this from device locale
           
           await SnappedAPI.initializeUser(deviceType, country);
           console.log('New anonymous user created');
         } else {
           console.log('Existing user loaded:', existingUserId);
         }
       } catch (error) {
         console.error('Error initializing app:', error);
       }
     };
   
     const setupPushNotifications = () => {
       PushNotification.configure({
         onNotification: function(notification) {
           console.log('Notification received:', notification);
           
           // Handle ticket resolution notifications
           if (notification.data && notification.data.type === 'ticket_resolved') {
             // Navigate to ticket results or show success message
             handleTicketResolved(notification.data.ticket_id);
           }
         },
         requestPermissions: Platform.OS === 'ios',
       });
     };
   
     const handleTicketResolved = (ticketId) => {
       // Navigate to ticket details or show success message
       console.log('Ticket resolved:', ticketId);
       // You can navigate to a specific screen or show an alert
     };
   
     return (
       // Your app components
     );
   };
   
   export default App;
   ```

4. **Search Screen Implementation:**
   ```javascript
   // screens/SearchScreen.js
   import React, { useState } from 'react';
   import { View, Text, TouchableOpacity, Image, Alert, ScrollView } from 'react-native';
   import { launchImageLibrary } from 'react-native-image-picker';
   import SnappedAPI from '../services/api';
   
   const SearchScreen = () => {
     const [searchResults, setSearchResults] = useState([]);
     const [loading, setLoading] = useState(false);
     const [currentSearchId, setCurrentSearchId] = useState(null);
   
     const selectImage = () => {
       launchImageLibrary({ mediaType: 'photo', quality: 0.8 }, (response) => {
         if (response.assets && response.assets[0]) {
           performImageSearch(response.assets[0].uri);
         }
       });
     };
   
     const performImageSearch = async (imageUri) => {
       try {
         setLoading(true);
         const results = await SnappedAPI.searchByImage(imageUri);
         setSearchResults(results.results || []);
         setCurrentSearchId(results.search_id);
       } catch (error) {
         Alert.alert('Error', 'Failed to search for products');
       } finally {
         setLoading(false);
       }
     };
   
     const performTextSearch = async (query) => {
       try {
         setLoading(true);
         const results = await SnappedAPI.searchByText(query);
         setSearchResults(results.results || []);
         setCurrentSearchId(results.search_id);
       } catch (error) {
         Alert.alert('Error', 'Failed to search for products');
       } finally {
         setLoading(false);
       }
     };
   
     const handleProductClick = async (result, index) => {
       try {
         // Record click for analytics
         await SnappedAPI.recordClick(
           currentSearchId,
           result.id,
           result.partner_domain || 'unknown',
           result.partner_name || result.source,
           result.brand,
           result.title,
           result.price,
           index + 1
         );
   
         // Open product link
         // Linking.openURL(result.link);
       } catch (error) {
         console.error('Error recording click:', error);
       }
     };
   
     const submitTicket = async () => {
       try {
         Alert.prompt(
           'Need Help?',
           'Describe what you\'re looking for and we\'ll help you find it:',
           async (userNote) => {
             if (userNote) {
               await SnappedAPI.submitTicket(
                 currentSearchId,
                 userNote,
                 'https://example.com/crop.jpg', // Replace with actual crop image URL
                 'https://example.com/original.jpg' // Replace with actual original image URL
               );
               Alert.alert('Success', 'Your request has been submitted. We\'ll notify you when we find your item!');
             }
           }
         );
       } catch (error) {
         Alert.alert('Error', 'Failed to submit request');
       }
     };
   
     return (
       <ScrollView style={{ flex: 1, padding: 16 }}>
         <TouchableOpacity onPress={selectImage} style={styles.searchButton}>
           <Text>Search by Image</Text>
         </TouchableOpacity>
   
         {/* Search Results */}
         {searchResults.map((result, index) => (
           <TouchableOpacity
             key={result.id}
             onPress={() => handleProductClick(result, index)}
             style={styles.resultItem}
           >
             <Image source={{ uri: result.image_url }} style={styles.resultImage} />
             <View style={styles.resultInfo}>
               <Text style={styles.resultTitle}>{result.title}</Text>
               <Text style={styles.resultPrice}>{result.price}</Text>
               <Text style={styles.resultBrand}>{result.brand}</Text>
             </View>
           </TouchableOpacity>
         ))}
   
         {/* Ticket Submission Button - Always at bottom */}
         {searchResults.length > 0 && (
           <TouchableOpacity onPress={submitTicket} style={styles.ticketButton}>
             <Text style={styles.ticketButtonText}>Can't find what you're looking for?</Text>
             <Text style={styles.ticketButtonSubtext}>Let our specialists help you</Text>
           </TouchableOpacity>
         )}
       </ScrollView>
     );
   };
   
   const styles = {
     searchButton: {
       backgroundColor: '#007AFF',
       padding: 16,
       borderRadius: 8,
       alignItems: 'center',
       marginBottom: 16,
     },
     resultItem: {
       flexDirection: 'row',
       padding: 12,
       borderBottomWidth: 1,
       borderBottomColor: '#eee',
     },
     resultImage: {
       width: 80,
       height: 80,
       borderRadius: 8,
     },
     resultInfo: {
       flex: 1,
       marginLeft: 12,
     },
     resultTitle: {
       fontSize: 16,
       fontWeight: 'bold',
     },
     resultPrice: {
       fontSize: 14,
       color: '#007AFF',
       marginTop: 4,
     },
     resultBrand: {
       fontSize: 12,
       color: '#666',
       marginTop: 2,
     },
     ticketButton: {
       backgroundColor: '#FF6B6B',
       padding: 16,
       borderRadius: 8,
       alignItems: 'center',
       marginTop: 20,
       marginBottom: 20,
     },
     ticketButtonText: {
       color: 'white',
       fontSize: 16,
       fontWeight: 'bold',
     },
     ticketButtonSubtext: {
       color: 'white',
       fontSize: 12,
       marginTop: 4,
     },
   };
   
   export default SearchScreen;
   ```

5. **Push Notification Setup:**
   ```javascript
   // services/pushNotifications.js
   import PushNotification from 'react-native-push-notification';
   import { Platform } from 'react-native';
   
   class PushNotificationService {
     configure = () => {
       PushNotification.configure({
         onRegister: function(token) {
           console.log('Push notification token:', token);
           // Send token to your backend if needed
         },
   
         onNotification: function(notification) {
           console.log('Notification received:', notification);
           
           if (notification.data && notification.data.type === 'ticket_resolved') {
             // Handle ticket resolution notification
             PushNotification.localNotification({
               title: 'Item Found!',
               message: 'One of our specialists sourced an item for you.',
               playSound: true,
               soundName: 'default',
             });
           }
         },
   
         permissions: {
           alert: true,
           badge: true,
           sound: true,
         },
   
         popInitialNotification: true,
         requestPermissions: Platform.OS === 'ios',
       });
     };
   }
   
   export default new PushNotificationService();
   ```

### Key Integration Points:

1. **App Launch**: Create anonymous user immediately
2. **Search Results**: Add ticket submission button at bottom
3. **Click Tracking**: Record all user interactions for analytics
4. **Push Notifications**: Handle ticket resolution notifications
5. **Error Handling**: Graceful fallbacks for network issues

### Testing Your Integration:

1. **Test User Creation**: Verify anonymous user is created on app launch
2. **Test Search**: Try both image and text search functionality
3. **Test Ticket Submission**: Submit a test ticket and verify it appears in admin panel
4. **Test Push Notifications**: Resolve a ticket in admin panel and verify notification is received

## 📚 API Documentation

Once the application is running, you can access the comprehensive API documentation at:
- **Swagger UI**: `http://localhost:12000/docs`
- **ReDoc**: `http://localhost:12000/redoc`
- **Implementation Guide**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🔧 Technical Specifications

### Python Compatibility
- Python 3.9+
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13 (using SQLAlchemy 1.4)

### Performance Optimization

1. **Asynchronous Architecture**:
   - Async/await throughout the application
   - Non-blocking I/O operations
   - Background task processing
   - Connection pooling for external APIs

2. **Database Optimization**:
   - Optimized indexes for analytics queries
   - Efficient pagination for large datasets
   - Foreign key relationships for data integrity
   - SQLite optimizations (WAL mode, memory-mapped I/O)

3. **Caching & Storage**:
   - In-memory caching for development
   - Redis caching support for production
   - Cloudinary integration for image storage
   - Local storage fallback options

4. **Monitoring & Analytics**:
   - Request timing middleware
   - Performance logging and metrics
   - Real-time analytics dashboard
   - User behavior tracking

5. **Security & Resilience**:
   - Input validation and sanitization
   - CORS configuration
   - Rate limiting framework
   - Graceful error handling
   - Circuit breaker pattern for external APIs

## 🖼️ Image Storage & Processing

### Storage Options
1. **Local Storage** (development):
   - Images stored in `app/static/uploads`
   - Simple setup, no external dependencies

2. **Cloudinary Integration** (production):
   - CDN distribution for global access
   - Image transformations and optimizations
   - Direct cropping capabilities
   - Automatic backup and redundancy

### Configuration
```env
# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
USE_CLOUDINARY=true
```

## 🚀 Deployment & Production

### Environment Variables
```env
# Core Configuration
SERPAPI_API_KEY=your_serpapi_key
GOOGLE_VISION_API_KEY=your_vision_key
DATABASE_URL=sqlite:///./app.db

# Push Notifications
FCM_SERVER_KEY=your_fcm_key
APNS_KEY_ID=your_apns_key_id
APNS_TEAM_ID=your_apns_team_id

# Image Storage
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Production Optimizations
- Redis caching for improved performance
- Database connection pooling
- Async processing for all operations
- Comprehensive error handling and logging
- Security headers and CORS configuration

### Docker Support
```bash
# Start with Docker Compose
docker-compose up -d

# Or run with Redis
./run_with_redis.sh
```

## 📊 Admin Panel Features

### Dashboard Analytics
- **Real-time Metrics**: Users, searches, clicks, CTR
- **Trend Analysis**: 7-day and 30-day performance charts
- **Partner Performance**: Top partners and revenue sources
- **User Behavior**: Engagement patterns and retention

### Management Tools
- **Search Management**: Filter and analyze all searches
- **Click Analytics**: Partner performance and user engagement
- **User Tracking**: Anonymous user behavior and preferences
- **Ticket System**: Support request management with notifications
- **Affiliate Management**: Partner link optimization

### Data Export
- CSV export for all analytics data
- Filterable by date, partner, device, country
- Comprehensive reporting for business intelligence

## 🔐 Security & Privacy

### Anonymous User System
- No personal data collection required
- UUID-based tracking for privacy
- Local preference storage
- GDPR-compliant design

### Security Features
- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- Rate limiting
- Security headers
- Encrypted API communications

## 📈 Analytics & Insights

### User Analytics
- Device type and country tracking
- Search behavior patterns
- Click-through rates by partner
- User engagement metrics

### Business Intelligence
- Revenue optimization through affiliate tracking
- Partner performance analysis
- Search quality metrics
- Support ticket resolution analytics

## 🛠️ Development & Testing

### Testing
```bash
# Run tests
python -m pytest tests/

# Performance benchmarking
python benchmark.py --requests 100 --concurrent 10
```

### Development Tools
- Comprehensive API documentation at `/docs`
- Request timing and performance monitoring
- Detailed error logging and debugging
- Hot reload for development

## 📞 Support & Documentation

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Interactive API Docs**: `http://localhost:12000/docs`
- **Alternative Docs**: `http://localhost:12000/redoc`

## 🎯 Business Benefits

### User Experience
- **Instant Access**: No sign-up barriers
- **Smart Search**: Both visual and text-based search
- **Expert Support**: Ticket system with specialist help
- **Real-time Updates**: Push notifications for ticket resolution

### Revenue Optimization
- **Affiliate Tracking**: Complete click and conversion tracking
- **Partner Analytics**: Performance-based partner management
- **User Insights**: Behavior analysis for optimization
- **Conversion Optimization**: CTR tracking and improvement

### Operational Efficiency
- **Admin Dashboard**: Complete business overview
- **Automated Support**: Ticket system with notifications
- **Analytics**: Data-driven decision making
- **Scalable Architecture**: Ready for growth