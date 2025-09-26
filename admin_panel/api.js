// API Service for Admin Panel
class AdminAPI {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // POST with FormData
    async postFormData(endpoint, formData) {
        return this.request(endpoint, {
            method: 'POST',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData
        });
    }

    // PUT with FormData
    async putFormData(endpoint, formData) {
        return this.request(endpoint, {
            method: 'PUT',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData
        });
    }

    // Dashboard API
    async getDashboard(startDate = null, endDate = null) {
        const params = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        return this.get('/admin/dashboard', params);
    }

    // Searches API
    async getSearches(page = 1, perPage = CONFIG.DEFAULT_PAGE_SIZE, filters = {}) {
        const params = {
            page,
            per_page: perPage,
            ...filters
        };
        return this.get('/admin/searches', params);
    }

    async getSearchDetail(searchId) {
        return this.get(`/admin/searches/${searchId}`);
    }

    // Clicks API
    async getClicks(page = 1, perPage = CONFIG.DEFAULT_PAGE_SIZE, filters = {}) {
        const params = {
            page,
            per_page: perPage,
            ...filters
        };
        return this.get('/admin/clicks', params);
    }

    // Partners API
    async getPartners(startDate = null, endDate = null) {
        const params = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        return this.get('/admin/partners', params);
    }

    // Users API
    async getUsers(page = 1, perPage = CONFIG.DEFAULT_PAGE_SIZE, filters = {}) {
        const params = {
            page,
            per_page: perPage,
            ...filters
        };
        return this.get('/admin/users', params);
    }

    async getUserDetail(userId) {
        return this.get(`/admin/users/${userId}`);
    }

    // Tickets API
    async getTickets(page = 1, perPage = CONFIG.DEFAULT_PAGE_SIZE, filters = {}) {
        const params = {
            page,
            per_page: perPage,
            ...filters
        };
        return this.get('/admin/tickets', params);
    }

    async getTicketDetail(ticketId) {
        return this.get(`/admin/tickets/${ticketId}`);
    }

    async updateTicket(ticketId, data) {
        const formData = new FormData();
        
        Object.keys(data).forEach(key => {
            if (data[key] !== null && data[key] !== undefined) {
                formData.append(key, data[key]);
            }
        });

        return this.putFormData(`/admin/tickets/${ticketId}`, formData);
    }

    // Affiliate Links API
    async getAffiliateLinks() {
        return this.get('/admin/affiliate-links');
    }

    async createAffiliateLink(data) {
        return this.post('/admin/affiliate-links', data);
    }

    async updateAffiliateLink(linkId, data) {
        return this.put(`/admin/affiliate-links/${linkId}`, data);
    }

    async deleteAffiliateLink(linkId) {
        return this.delete(`/admin/affiliate-links/${linkId}`);
    }

    // Export data
    async exportData(endpoint, filters = {}) {
        const params = {
            ...filters,
            export: 'csv',
            per_page: CONFIG.EXPORT.maxRecords
        };
        return this.get(endpoint, params);
    }

    // Health check
    async healthCheck() {
        return this.get('/health');
    }
}

// Loading state management
class LoadingManager {
    constructor() {
        this.loadingStates = new Set();
        this.overlay = document.getElementById('loading-overlay');
    }

    show(key = 'default') {
        this.loadingStates.add(key);
        if (this.overlay) {
            this.overlay.style.display = 'flex';
        }
    }

    hide(key = 'default') {
        this.loadingStates.delete(key);
        if (this.loadingStates.size === 0 && this.overlay) {
            this.overlay.style.display = 'none';
        }
    }

    hideAll() {
        this.loadingStates.clear();
        if (this.overlay) {
            this.overlay.style.display = 'none';
        }
    }
}

// Error handling
class ErrorHandler {
    static handle(error, context = '') {
        console.error(`Error in ${context}:`, error);
        
        let message = 'An unexpected error occurred';
        
        if (error.message) {
            message = error.message;
        } else if (typeof error === 'string') {
            message = error;
        }

        // Show user-friendly error message
        Utils.showNotification(message, 'error');
        
        // Log to external service in production
        if (window.location.hostname !== 'localhost') {
            // You can integrate with error tracking services like Sentry here
            console.log('Would log to external service:', { error, context });
        }
    }
}

// API wrapper with loading and error handling
class APIWrapper {
    constructor() {
        this.api = new AdminAPI();
        this.loading = new LoadingManager();
    }

    async execute(apiCall, loadingKey = 'default', showLoading = true) {
        try {
            if (showLoading) {
                this.loading.show(loadingKey);
            }
            
            const result = await apiCall();
            return result;
        } catch (error) {
            ErrorHandler.handle(error, loadingKey);
            throw error;
        } finally {
            if (showLoading) {
                this.loading.hide(loadingKey);
            }
        }
    }

    // Dashboard methods
    async getDashboard(startDate, endDate) {
        return this.execute(() => this.api.getDashboard(startDate, endDate), 'dashboard');
    }

    // Searches methods
    async getSearches(page, perPage, filters) {
        return this.execute(() => this.api.getSearches(page, perPage, filters), 'searches');
    }

    async getSearchDetail(searchId) {
        return this.execute(() => this.api.getSearchDetail(searchId), 'search-detail');
    }

    // Clicks methods
    async getClicks(page, perPage, filters) {
        return this.execute(() => this.api.getClicks(page, perPage, filters), 'clicks');
    }

    // Partners methods
    async getPartners(startDate, endDate) {
        return this.execute(() => this.api.getPartners(startDate, endDate), 'partners');
    }

    // Users methods
    async getUsers(page, perPage, filters) {
        return this.execute(() => this.api.getUsers(page, perPage, filters), 'users');
    }

    async getUserDetail(userId) {
        return this.execute(() => this.api.getUserDetail(userId), 'user-detail');
    }

    // Tickets methods
    async getTickets(page, perPage, filters) {
        return this.execute(() => this.api.getTickets(page, perPage, filters), 'tickets');
    }

    async getTicketDetail(ticketId) {
        return this.execute(() => this.api.getTicketDetail(ticketId), 'ticket-detail');
    }

    async updateTicket(ticketId, data) {
        return this.execute(() => this.api.updateTicket(ticketId, data), 'ticket-update');
    }

    // Affiliate Links methods
    async getAffiliateLinks() {
        return this.execute(() => this.api.getAffiliateLinks(), 'affiliate-links');
    }

    async createAffiliateLink(data) {
        return this.execute(() => this.api.createAffiliateLink(data), 'affiliate-create');
    }

    async updateAffiliateLink(linkId, data) {
        return this.execute(() => this.api.updateAffiliateLink(linkId, data), 'affiliate-update');
    }

    async deleteAffiliateLink(linkId) {
        return this.execute(() => this.api.deleteAffiliateLink(linkId), 'affiliate-delete');
    }

    // Export methods
    async exportSearches(filters) {
        return this.execute(() => this.api.exportData('/admin/searches', filters), 'export-searches');
    }

    async exportClicks(filters) {
        return this.execute(() => this.api.exportData('/admin/clicks', filters), 'export-clicks');
    }

    async exportUsers(filters) {
        return this.execute(() => this.api.exportData('/admin/users', filters), 'export-users');
    }

    async exportTickets(filters) {
        return this.execute(() => this.api.exportData('/admin/tickets', filters), 'export-tickets');
    }

    // Health check
    async healthCheck() {
        return this.execute(() => this.api.healthCheck(), 'health-check', false);
    }
}

// Create global API instance
window.adminAPI = new APIWrapper();

// Auto-refresh functionality
class AutoRefresh {
    constructor() {
        this.intervals = new Map();
        this.enabled = CONFIG.AUTO_REFRESH.enabled;
    }

    start(key, callback, interval) {
        if (!this.enabled) return;
        
        this.stop(key); // Clear existing interval
        
        const intervalId = setInterval(callback, interval);
        this.intervals.set(key, intervalId);
    }

    stop(key) {
        const intervalId = this.intervals.get(key);
        if (intervalId) {
            clearInterval(intervalId);
            this.intervals.delete(key);
        }
    }

    stopAll() {
        this.intervals.forEach((intervalId) => {
            clearInterval(intervalId);
        });
        this.intervals.clear();
    }

    toggle() {
        this.enabled = !this.enabled;
        if (!this.enabled) {
            this.stopAll();
        }
    }
}

// Create global auto-refresh instance
window.autoRefresh = new AutoRefresh();

// Connection status monitoring
class ConnectionMonitor {
    constructor() {
        this.isOnline = navigator.onLine;
        this.lastCheck = Date.now();
        this.checkInterval = 30000; // 30 seconds
        
        this.init();
    }

    init() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            Utils.showNotification('Connection restored', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            Utils.showNotification('Connection lost', 'warning');
        });

        // Periodic health check
        setInterval(() => {
            this.checkConnection();
        }, this.checkInterval);
    }

    async checkConnection() {
        try {
            await adminAPI.healthCheck();
            if (!this.isOnline) {
                this.isOnline = true;
                Utils.showNotification('Connection restored', 'success');
            }
        } catch (error) {
            if (this.isOnline) {
                this.isOnline = false;
                Utils.showNotification('Connection issues detected', 'warning');
            }
        }
        this.lastCheck = Date.now();
    }
}

// Initialize connection monitor
window.connectionMonitor = new ConnectionMonitor();