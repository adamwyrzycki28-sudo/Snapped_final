# React Native Integration Guide

This guide provides step-by-step instructions for integrating your React Native app with the enhanced Snapped AI FastAPI backend.

## 📱 Quick Start Checklist

- [ ] Install required React Native dependencies
- [ ] Create API service class
- [ ] Initialize anonymous user on app launch
- [ ] Implement search functionality (image + text)
- [ ] Add ticket submission to search results
- [ ] Set up push notifications
- [ ] Test all integration points

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
# Core dependencies
npm install @react-native-async-storage/async-storage
npm install react-native-image-picker

# Push notifications
npm install react-native-push-notification
npm install @react-native-community/push-notification-ios  # iOS only

# Optional: For better image handling
npm install react-native-image-resizer
npm install react-native-permissions
```

### 2. Platform-specific Setup

#### iOS Setup
```bash
cd ios && pod install
```

Add to `ios/YourApp/AppDelegate.m`:
```objc
#import <UserNotifications/UserNotifications.h>
#import <RNCPushNotificationIOS.h>

// Add this in didFinishLaunchingWithOptions
UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
center.delegate = self;
```

#### Android Setup
Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
```

## 🔧 Core Implementation

### 1. API Service Class

Create `services/SnappedAPI.js`:

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

class SnappedAPI {
  constructor() {
    this.baseURL = 'https://your-backend-url.com/api/v1';
    this.userId = null;
  }

  // Initialize anonymous user
  async initializeUser(deviceType, country) {
    try {
      const formData = new FormData();
      formData.append('device_type', deviceType);
      formData.append('country', country);

      const response = await fetch(`${this.baseURL}/users/create`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const user = await response.json();
      this.userId = user.user_id;
      
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

  // Image search
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

      const response = await fetch(`${this.baseURL}/images/search`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error searching by image:', error);
      throw error;
    }
  }

  // Text search
  async searchByText(query) {
    try {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('user_id', this.userId);

      const response = await fetch(`${this.baseURL}/images/search-by-text`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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

      const response = await fetch(`${this.baseURL}/images/detect-objects`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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

      const response = await fetch(`${this.baseURL}/users/${this.userId}/tickets`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

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

      const response = await fetch(`${this.baseURL}/users/${this.userId}/clicks`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error recording click:', error);
      // Don't throw error for analytics - fail silently
      return null;
    }
  }

  // Get user tickets
  async getUserTickets() {
    try {
      const response = await fetch(`${this.baseURL}/users/${this.userId}/tickets`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user tickets:', error);
      throw error;
    }
  }

  // Get search history
  async getSearchHistory(page = 1, perPage = 20) {
    try {
      const response = await fetch(
        `${this.baseURL}/images/searches?user_id=${this.userId}&page=${page}&per_page=${perPage}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting search history:', error);
      throw error;
    }
  }
}

export default new SnappedAPI();
```

### 2. App Initialization

Update your `App.js`:

```javascript
import React, { useEffect, useState } from 'react';
import { Platform, Alert } from 'react-native';
import SnappedAPI from './services/SnappedAPI';
import PushNotificationService from './services/PushNotificationService';

const App = () => {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize push notifications
      PushNotificationService.configure();

      // Try to load existing user ID
      const existingUserId = await SnappedAPI.loadUserId();
      
      if (!existingUserId) {
        // Create new anonymous user
        const deviceType = Platform.OS === 'ios' ? 'iOS' : 'Android';
        const country = 'US'; // You can get this from device locale or IP geolocation
        
        await SnappedAPI.initializeUser(deviceType, country);
        console.log('New anonymous user created');
      } else {
        console.log('Existing user loaded:', existingUserId);
      }

      setIsInitialized(true);
    } catch (error) {
      console.error('Error initializing app:', error);
      Alert.alert('Initialization Error', 'Failed to initialize app. Please try again.');
    }
  };

  if (!isInitialized) {
    return <LoadingScreen />; // Your loading component
  }

  return (
    <NavigationContainer>
      {/* Your app navigation */}
    </NavigationContainer>
  );
};

export default App;
```

### 3. Search Screen Implementation

Create `screens/SearchScreen.js`:

```javascript
import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  Alert,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Linking,
  StyleSheet,
} from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';
import SnappedAPI from '../services/SnappedAPI';

const SearchScreen = () => {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentSearchId, setCurrentSearchId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentImageUri, setCurrentImageUri] = useState(null);

  const selectImage = useCallback(() => {
    const options = {
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    };

    launchImageLibrary(options, (response) => {
      if (response.assets && response.assets[0]) {
        const imageUri = response.assets[0].uri;
        setCurrentImageUri(imageUri);
        performImageSearch(imageUri);
      }
    });
  }, []);

  const performImageSearch = async (imageUri) => {
    try {
      setLoading(true);
      setSearchResults([]);
      
      const results = await SnappedAPI.searchByImage(imageUri);
      setSearchResults(results.results || []);
      setCurrentSearchId(results.search_id);
    } catch (error) {
      Alert.alert('Search Error', 'Failed to search for products. Please try again.');
      console.error('Image search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const performTextSearch = async () => {
    if (!searchQuery.trim()) {
      Alert.alert('Invalid Query', 'Please enter a search term.');
      return;
    }

    try {
      setLoading(true);
      setSearchResults([]);
      
      const results = await SnappedAPI.searchByText(searchQuery.trim());
      setSearchResults(results.results || []);
      setCurrentSearchId(results.search_id);
      setCurrentImageUri(null);
    } catch (error) {
      Alert.alert('Search Error', 'Failed to search for products. Please try again.');
      console.error('Text search error:', error);
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
      if (result.link) {
        await Linking.openURL(result.link);
      }
    } catch (error) {
      console.error('Error handling product click:', error);
      // Still try to open the link even if analytics fails
      if (result.link) {
        await Linking.openURL(result.link);
      }
    }
  };

  const submitTicket = async () => {
    Alert.prompt(
      'Need Help Finding This Item?',
      'Describe what you\'re looking for and our specialists will help you find it:',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Submit',
          onPress: async (userNote) => {
            if (userNote && userNote.trim()) {
              try {
                await SnappedAPI.submitTicket(
                  currentSearchId,
                  userNote.trim(),
                  currentImageUri || 'text_search',
                  currentImageUri
                );
                Alert.alert(
                  'Request Submitted!',
                  'Your request has been submitted. We\'ll notify you when we find your item!'
                );
              } catch (error) {
                Alert.alert('Submission Error', 'Failed to submit request. Please try again.');
                console.error('Ticket submission error:', error);
              }
            }
          },
        },
      ],
      'plain-text'
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Search Controls */}
      <View style={styles.searchControls}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by text..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={performTextSearch}
        />
        <TouchableOpacity onPress={performTextSearch} style={styles.textSearchButton}>
          <Text style={styles.buttonText}>Search</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity onPress={selectImage} style={styles.imageSearchButton}>
        <Text style={styles.buttonText}>Search by Image</Text>
      </TouchableOpacity>

      {/* Loading Indicator */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Searching...</Text>
        </View>
      )}

      {/* Current Image Preview */}
      {currentImageUri && (
        <View style={styles.imagePreview}>
          <Image source={{ uri: currentImageUri }} style={styles.previewImage} />
        </View>
      )}

      {/* Search Results */}
      {searchResults.map((result, index) => (
        <TouchableOpacity
          key={`${result.id}-${index}`}
          onPress={() => handleProductClick(result, index)}
          style={styles.resultItem}
        >
          {result.image_url && (
            <Image source={{ uri: result.image_url }} style={styles.resultImage} />
          )}
          <View style={styles.resultInfo}>
            <Text style={styles.resultTitle} numberOfLines={2}>
              {result.title}
            </Text>
            {result.price && (
              <Text style={styles.resultPrice}>{result.price}</Text>
            )}
            {result.brand && (
              <Text style={styles.resultBrand}>{result.brand}</Text>
            )}
            {result.source && (
              <Text style={styles.resultSource}>from {result.source}</Text>
            )}
          </View>
        </TouchableOpacity>
      ))}

      {/* No Results Message */}
      {!loading && searchResults.length === 0 && currentSearchId && (
        <View style={styles.noResultsContainer}>
          <Text style={styles.noResultsText}>No results found</Text>
          <Text style={styles.noResultsSubtext}>Try a different search or let our specialists help you</Text>
        </View>
      )}

      {/* Ticket Submission Button */}
      {(searchResults.length > 0 || (!loading && currentSearchId)) && (
        <TouchableOpacity onPress={submitTicket} style={styles.ticketButton}>
          <Text style={styles.ticketButtonText}>Can't find what you're looking for?</Text>
          <Text style={styles.ticketButtonSubtext}>Let our specialists help you</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  searchControls: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  searchInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: 'white',
    marginRight: 8,
  },
  textSearchButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  imageSearchButton: {
    backgroundColor: '#34C759',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  imagePreview: {
    alignItems: 'center',
    marginBottom: 16,
  },
  previewImage: {
    width: 200,
    height: 200,
    borderRadius: 8,
  },
  resultItem: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  resultImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  resultInfo: {
    flex: 1,
    marginLeft: 12,
    justifyContent: 'center',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  resultPrice: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
    marginBottom: 2,
  },
  resultBrand: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  resultSource: {
    fontSize: 12,
    color: '#999',
  },
  noResultsContainer: {
    alignItems: 'center',
    padding: 40,
  },
  noResultsText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#666',
    marginBottom: 8,
  },
  noResultsSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
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
});

export default SearchScreen;
```

### 4. Push Notification Service

Create `services/PushNotificationService.js`:

```javascript
import PushNotification from 'react-native-push-notification';
import { Platform } from 'react-native';

class PushNotificationService {
  configure = () => {
    PushNotification.configure({
      onRegister: (token) => {
        console.log('Push notification token:', token);
        // You can send this token to your backend if needed for targeted notifications
      },

      onNotification: (notification) => {
        console.log('Notification received:', notification);
        
        // Handle different notification types
        if (notification.data && notification.data.type === 'ticket_resolved') {
          this.handleTicketResolved(notification);
        }

        // Required on iOS only
        if (Platform.OS === 'ios') {
          notification.finish(PushNotificationIOS.FetchResult.NoData);
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

  handleTicketResolved = (notification) => {
    // Show local notification
    PushNotification.localNotification({
      title: 'Item Found!',
      message: 'One of our specialists sourced an item for you.',
      playSound: true,
      soundName: 'default',
      userInfo: notification.data,
    });

    // You can also navigate to a specific screen here
    // NavigationService.navigate('TicketDetails', { ticketId: notification.data.ticket_id });
  };

  // Method to show local notifications
  showLocalNotification = (title, message, data = {}) => {
    PushNotification.localNotification({
      title,
      message,
      playSound: true,
      soundName: 'default',
      userInfo: data,
    });
  };
}

export default new PushNotificationService();
```

## 🧪 Testing Your Integration

### 1. Test User Creation
```javascript
// In your test file or development console
import SnappedAPI from './services/SnappedAPI';

const testUserCreation = async () => {
  try {
    const user = await SnappedAPI.initializeUser('iOS', 'US');
    console.log('User created:', user);
  } catch (error) {
    console.error('User creation failed:', error);
  }
};
```

### 2. Test Search Functionality
```javascript
const testSearch = async () => {
  try {
    // Test text search
    const textResults = await SnappedAPI.searchByText('Nike shoes');
    console.log('Text search results:', textResults);

    // Test image search (you'll need a valid image URI)
    // const imageResults = await SnappedAPI.searchByImage('file://path/to/image.jpg');
    // console.log('Image search results:', imageResults);
  } catch (error) {
    console.error('Search failed:', error);
  }
};
```

### 3. Test Ticket Submission
```javascript
const testTicketSubmission = async () => {
  try {
    const ticket = await SnappedAPI.submitTicket(
      1, // searchId
      'Looking for vintage Nike Air Jordan 1985',
      'https://example.com/crop.jpg',
      'https://example.com/original.jpg'
    );
    console.log('Ticket submitted:', ticket);
  } catch (error) {
    console.error('Ticket submission failed:', error);
  }
};
```

## 🔧 Advanced Features

### 1. Image Cropping Integration
```javascript
// If you want to add image cropping before search
import ImagePicker from 'react-native-image-crop-picker';

const selectAndCropImage = () => {
  ImagePicker.openPicker({
    width: 400,
    height: 400,
    cropping: true,
    cropperCircleOverlay: false,
    compressImageMaxWidth: 1024,
    compressImageMaxHeight: 1024,
    compressImageQuality: 0.8,
  }).then(image => {
    performImageSearch(image.path);
  });
};
```

### 2. Offline Support
```javascript
import NetInfo from '@react-native-community/netinfo';

const checkConnectivity = async () => {
  const state = await NetInfo.fetch();
  return state.isConnected;
};

// Use in your API calls
const searchWithConnectivityCheck = async (query) => {
  const isConnected = await checkConnectivity();
  if (!isConnected) {
    Alert.alert('No Internet', 'Please check your internet connection and try again.');
    return;
  }
  
  return await SnappedAPI.searchByText(query);
};
```

### 3. Search History Screen
```javascript
const SearchHistoryScreen = () => {
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSearchHistory();
  }, []);

  const loadSearchHistory = async () => {
    try {
      const history = await SnappedAPI.getSearchHistory();
      setSearchHistory(history.searches || []);
    } catch (error) {
      console.error('Error loading search history:', error);
    } finally {
      setLoading(false);
    }
  };

  // Render search history items...
};
```

## 🚀 Production Considerations

### 1. Error Handling
- Implement comprehensive error handling for network failures
- Add retry logic for failed API calls
- Show user-friendly error messages

### 2. Performance Optimization
- Implement image compression before upload
- Add loading states for better UX
- Cache search results locally when appropriate

### 3. Analytics
- Track user interactions for business intelligence
- Monitor API response times
- Log errors for debugging

### 4. Security
- Validate all user inputs
- Use HTTPS for all API calls
- Store sensitive data securely

## 📞 Support

If you encounter any issues during integration:

1. Check the API documentation at `http://your-backend-url/docs`
2. Review the implementation summary in `IMPLEMENTATION_SUMMARY.md`
3. Test individual API endpoints using the interactive documentation
4. Check server logs for detailed error information

## 🎯 Next Steps

After completing the basic integration:

1. **Customize UI/UX** to match your app's design
2. **Add advanced features** like image cropping, filters, favorites
3. **Implement analytics** to track user behavior
4. **Add offline support** for better user experience
5. **Optimize performance** based on usage patterns
6. **Set up push notification certificates** for production

Your React Native app is now ready to leverage all the powerful features of the enhanced Snapped AI backend!