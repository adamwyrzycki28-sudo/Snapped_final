# Snapped AI Admin Panel

A modern, responsive HTML/CSS/JavaScript admin panel for managing the Snapped AI FastAPI backend.

## 🚀 Features

### Dashboard
- **Real-time Metrics**: Total searches, clicks, users, and CTR
- **Interactive Charts**: 7-day and 30-day trend analysis using Chart.js
- **Top Partners & Sources**: Performance rankings and analytics
- **Auto-refresh**: Automatic data updates every 30 seconds

### Ticket Management
- **Complete Ticket Lifecycle**: View, update, and resolve support tickets
- **Status Management**: Open, In Progress, Resolved states
- **Image Preview**: View user-submitted images directly in the interface
- **Real-time Updates**: Live ticket count badges and notifications
- **Bulk Actions**: Efficient ticket resolution workflows

### Advanced Features
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Mode Support**: Automatic theme detection and switching
- **Real-time Notifications**: Success, error, and warning messages
- **Export Functionality**: CSV export for all data tables
- **Search & Filtering**: Advanced filtering across all data views
- **Pagination**: Efficient handling of large datasets

## 📁 File Structure

```
admin_panel/
├── index.html          # Main HTML structure
├── styles.css          # Complete CSS styling with responsive design
├── config.js           # Configuration and utility functions
├── api.js              # API service layer with error handling
├── charts.js           # Chart.js integration and management
├── app.js              # Main application logic
└── README.md           # This documentation
```

## 🛠️ Setup Instructions

### 1. Basic Setup

1. **Copy the admin panel files** to your web server or local development environment
2. **Update the API URL** in `config.js`:
   ```javascript
   CONFIG.API_BASE_URL = 'http://your-backend-url.com/api/v1';
   ```
3. **Open `index.html`** in your web browser

### 2. Development Setup

For local development with live reload:

```bash
# Using Python's built-in server
cd admin_panel
python -m http.server 8080

# Using Node.js live-server
npm install -g live-server
live-server --port=8080
```

### 3. Production Deployment

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName admin.snapped.ai
    DocumentRoot /var/www/admin_panel
    
    <Directory /var/www/admin_panel>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name admin.snapped.ai;
    root /var/www/admin_panel;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Enable gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

## ⚙️ Configuration

### API Configuration
Update `config.js` to match your backend setup:

```javascript
const CONFIG = {
    // Update this to your FastAPI backend URL
    API_BASE_URL: 'http://localhost:12000/api/v1',
    
    // Pagination settings
    DEFAULT_PAGE_SIZE: 50,
    MAX_PAGE_SIZE: 100,
    
    // Auto-refresh intervals (milliseconds)
    DASHBOARD_REFRESH_INTERVAL: 30000,
    TICKET_REFRESH_INTERVAL: 10000,
    
    // Chart colors
    CHART_COLORS: {
        primary: '#667eea',
        secondary: '#764ba2',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444'
    }
};
```

### Environment-Specific URLs
The panel automatically detects the environment:

- **Development**: `http://localhost:12000/api/v1`
- **Staging**: `https://staging-api.snapped.ai/api/v1`
- **Production**: `https://api.snapped.ai/api/v1`

## 🎯 Usage Guide

### Dashboard Overview
1. **Access the dashboard** at the main URL
2. **View key metrics** in the stats cards at the top
3. **Analyze trends** using the interactive charts
4. **Monitor top performers** in the partner and source tables
5. **Apply date filters** to focus on specific time periods

### Ticket Management
1. **Navigate to Tickets** section from the sidebar
2. **Filter tickets** by status, user ID, or date range
3. **Click "View"** on any ticket to see full details
4. **Update ticket status** and add admin notes
5. **Resolve tickets** to trigger push notifications to users

### Advanced Features

#### Filtering and Search
- Use the filter inputs at the top of each section
- Filters are applied automatically with debouncing
- Combine multiple filters for precise data views

#### Data Export
- Click export buttons to download CSV files
- All current filters are applied to exports
- Maximum 10,000 records per export

#### Real-time Updates
- Dashboard refreshes every 30 seconds
- Ticket counts update every 10 seconds
- Manual refresh available via browser reload

## 🔧 Customization

### Styling
Modify `styles.css` to customize the appearance:

```css
/* Update primary colors */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
}
```

### Adding New Sections
1. **Add HTML structure** in `index.html`
2. **Create API methods** in `api.js`
3. **Implement loading logic** in `app.js`
4. **Add navigation** to the sidebar

### Custom Charts
Add new charts using Chart.js:

```javascript
// In charts.js
createCustomChart(data) {
    const chartData = {
        labels: data.labels,
        datasets: [{
            label: 'Custom Data',
            data: data.values,
            backgroundColor: CONFIG.CHART_COLORS.primary
        }]
    };
    
    return this.createChart('custom-chart', 'bar', chartData);
}
```

## 📱 Mobile Responsiveness

The admin panel is fully responsive and includes:

- **Collapsible sidebar** on mobile devices
- **Touch-friendly buttons** and form controls
- **Optimized table layouts** with horizontal scrolling
- **Responsive charts** that adapt to screen size
- **Mobile-first CSS** with progressive enhancement

## 🔒 Security Considerations

### Authentication
Currently, the panel doesn't include authentication. For production use:

1. **Add authentication layer** (OAuth, JWT, etc.)
2. **Implement role-based access** control
3. **Use HTTPS** for all communications
4. **Add CSRF protection** for form submissions

### API Security
- Ensure your FastAPI backend has proper authentication
- Use API keys or JWT tokens for admin endpoints
- Implement rate limiting on the backend
- Validate all user inputs

## 🐛 Troubleshooting

### Common Issues

#### API Connection Errors
```javascript
// Check browser console for errors
// Verify API_BASE_URL in config.js
// Ensure backend is running and accessible
```

#### Charts Not Loading
```javascript
// Verify Chart.js CDN is accessible
// Check browser console for JavaScript errors
// Ensure canvas elements exist in HTML
```

#### Mobile Layout Issues
```css
/* Check viewport meta tag in HTML */
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Debug Mode
Enable debug logging:

```javascript
// In config.js
CONFIG.DEBUG = true;

// This will log all API requests and responses
```

## 🚀 Performance Optimization

### Loading Performance
- **Minify CSS/JS** for production
- **Enable gzip compression** on web server
- **Use CDN** for external libraries
- **Implement caching** headers

### Runtime Performance
- **Debounced filters** prevent excessive API calls
- **Pagination** limits data transfer
- **Auto-refresh** can be disabled if needed
- **Chart animations** can be reduced for better performance

## 📊 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 90+

## 🔄 Updates and Maintenance

### Regular Updates
1. **Monitor API changes** in the FastAPI backend
2. **Update Chart.js** and other dependencies regularly
3. **Test responsive design** on new devices
4. **Review and update** security measures

### Backup and Recovery
- **Version control** all customizations
- **Document configuration** changes
- **Test backup procedures** regularly
- **Monitor error logs** for issues

## 📞 Support

For issues and questions:

1. **Check the browser console** for JavaScript errors
2. **Verify API connectivity** using browser dev tools
3. **Review configuration** in `config.js`
4. **Test with different browsers** to isolate issues

## 🎉 Features in Development

- **User authentication** and role management
- **Advanced analytics** with custom date ranges
- **Bulk operations** for ticket management
- **Email notifications** for critical events
- **API rate limiting** dashboard
- **System health monitoring**

The admin panel provides a comprehensive interface for managing your Snapped AI backend with a modern, user-friendly design that scales from mobile to desktop.