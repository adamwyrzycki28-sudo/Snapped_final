// Configuration for the Admin Panel
const CONFIG = {
    // API Base URL - Update this to match your FastAPI backend
    API_BASE_URL: 'http://localhost:12000/api/v1',
    
    // Pagination settings
    DEFAULT_PAGE_SIZE: 50,
    MAX_PAGE_SIZE: 100,
    
    // Refresh intervals (in milliseconds)
    DASHBOARD_REFRESH_INTERVAL: 30000, // 30 seconds
    TICKET_REFRESH_INTERVAL: 10000,    // 10 seconds
    
    // Chart colors
    CHART_COLORS: {
        primary: '#667eea',
        secondary: '#764ba2',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6'
    },
    
    // Date format options
    DATE_FORMAT_OPTIONS: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    },
    
    // Status colors
    STATUS_COLORS: {
        open: '#f59e0b',
        'in-progress': '#3b82f6',
        resolved: '#10b981'
    },
    
    // Default date range (days)
    DEFAULT_DATE_RANGE: 30,
    
    // Auto-refresh settings
    AUTO_REFRESH: {
        enabled: true,
        dashboard: 30000,  // 30 seconds
        tickets: 10000,    // 10 seconds
        searches: 60000,   // 1 minute
        clicks: 60000,     // 1 minute
        users: 300000,     // 5 minutes
        partners: 300000   // 5 minutes
    },
    
    // Image preview settings
    IMAGE_PREVIEW: {
        maxWidth: 200,
        maxHeight: 200,
        quality: 0.8
    },
    
    // Table settings
    TABLE_SETTINGS: {
        maxCellLength: 50,
        showRowNumbers: true,
        highlightOnHover: true
    },
    
    // Notification settings
    NOTIFICATIONS: {
        duration: 5000,
        position: 'top-right'
    },
    
    // Export settings
    EXPORT: {
        formats: ['csv', 'json'],
        maxRecords: 10000
    }
};

// Environment-specific overrides
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Development environment
    CONFIG.API_BASE_URL = 'http://localhost:12000/api/v1';
} else if (window.location.hostname.includes('staging')) {
    // Staging environment
    CONFIG.API_BASE_URL = 'https://staging-api.snapped.ai/api/v1';
} else {
    // Production environment
    CONFIG.API_BASE_URL = 'https://api.snapped.ai/api/v1';
}

// Utility functions
const Utils = {
    // Format date
    formatDate: (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', CONFIG.DATE_FORMAT_OPTIONS);
    },
    
    // Format number with commas
    formatNumber: (num) => {
        if (num === null || num === undefined) return '0';
        return num.toLocaleString();
    },
    
    // Format percentage
    formatPercentage: (num, decimals = 1) => {
        if (num === null || num === undefined) return '0%';
        return `${num.toFixed(decimals)}%`;
    },
    
    // Format currency
    formatCurrency: (amount, currency = 'USD') => {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Truncate text
    truncateText: (text, maxLength = CONFIG.TABLE_SETTINGS.maxCellLength) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },
    
    // Get status color
    getStatusColor: (status) => {
        return CONFIG.STATUS_COLORS[status] || '#64748b';
    },
    
    // Generate random ID
    generateId: () => {
        return Math.random().toString(36).substr(2, 9);
    },
    
    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Show notification
    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, CONFIG.NOTIFICATIONS.duration);
    },
    
    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            Utils.showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
            Utils.showNotification('Failed to copy to clipboard', 'error');
        }
    },
    
    // Download data as CSV
    downloadCSV: (data, filename) => {
        if (!data || data.length === 0) {
            Utils.showNotification('No data to export', 'warning');
            return;
        }
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => {
                const value = row[header];
                // Escape commas and quotes
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            }).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        Utils.showNotification('Data exported successfully!', 'success');
    },
    
    // Get date range
    getDateRange: (days = CONFIG.DEFAULT_DATE_RANGE) => {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        
        return {
            start: startDate.toISOString().split('T')[0],
            end: endDate.toISOString().split('T')[0]
        };
    },
    
    // Validate email
    isValidEmail: (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Validate URL
    isValidUrl: (url) => {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    },
    
    // Get relative time
    getRelativeTime: (dateString) => {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        
        return Utils.formatDate(dateString);
    },
    
    // Storage helpers
    storage: {
        set: (key, value) => {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.error('Failed to save to localStorage:', e);
            }
        },
        
        get: (key, defaultValue = null) => {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.error('Failed to read from localStorage:', e);
                return defaultValue;
            }
        },
        
        remove: (key) => {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.error('Failed to remove from localStorage:', e);
            }
        }
    }
};

// Export for use in other files
window.CONFIG = CONFIG;
window.Utils = Utils;