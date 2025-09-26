// Main Admin Panel Application
class AdminPanel {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentPage = {
            searches: 1,
            clicks: 1,
            users: 1,
            tickets: 1
        };
        this.filters = {
            dateRange: Utils.getDateRange(),
            searches: {},
            clicks: {},
            users: {},
            tickets: {}
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDateFilters();
        this.loadDashboard();
        this.startAutoRefresh();
        
        // Load initial data
        this.loadSection('dashboard');
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.switchSection(section);
            });
        });

        // Sidebar toggle for mobile
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('open');
            });
        }

        // Date filter
        document.getElementById('apply-filter').addEventListener('click', () => {
            this.applyDateFilter();
        });

        // Modal close buttons
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal.id);
            });
        });

        // Close modal when clicking outside
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Pagination buttons
        this.setupPaginationListeners();

        // Filter inputs
        this.setupFilterListeners();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupDateFilters() {
        const today = new Date();
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(today.getDate() - 30);

        document.getElementById('start-date').value = thirtyDaysAgo.toISOString().split('T')[0];
        document.getElementById('end-date').value = today.toISOString().split('T')[0];
    }

    setupPaginationListeners() {
        // Searches pagination
        document.getElementById('searches-prev').addEventListener('click', () => {
            if (this.currentPage.searches > 1) {
                this.currentPage.searches--;
                this.loadSearches();
            }
        });

        document.getElementById('searches-next').addEventListener('click', () => {
            this.currentPage.searches++;
            this.loadSearches();
        });

        // Clicks pagination
        document.getElementById('clicks-prev').addEventListener('click', () => {
            if (this.currentPage.clicks > 1) {
                this.currentPage.clicks--;
                this.loadClicks();
            }
        });

        document.getElementById('clicks-next').addEventListener('click', () => {
            this.currentPage.clicks++;
            this.loadClicks();
        });

        // Users pagination
        document.getElementById('users-prev').addEventListener('click', () => {
            if (this.currentPage.users > 1) {
                this.currentPage.users--;
                this.loadUsers();
            }
        });

        document.getElementById('users-next').addEventListener('click', () => {
            this.currentPage.users++;
            this.loadUsers();
        });

        // Tickets pagination
        document.getElementById('tickets-prev').addEventListener('click', () => {
            if (this.currentPage.tickets > 1) {
                this.currentPage.tickets--;
                this.loadTickets();
            }
        });

        document.getElementById('tickets-next').addEventListener('click', () => {
            this.currentPage.tickets++;
            this.loadTickets();
        });
    }

    setupFilterListeners() {
        // Debounced filter handlers
        const debouncedSearchFilter = Utils.debounce(() => this.loadSearches(), 500);
        const debouncedClickFilter = Utils.debounce(() => this.loadClicks(), 500);
        const debouncedUserFilter = Utils.debounce(() => this.loadUsers(), 500);
        const debouncedTicketFilter = Utils.debounce(() => this.loadTickets(), 500);

        // Search filters
        document.getElementById('search-user-filter').addEventListener('input', debouncedSearchFilter);
        document.getElementById('search-device-filter').addEventListener('change', debouncedSearchFilter);
        document.getElementById('search-country-filter').addEventListener('input', debouncedSearchFilter);

        // Click filters
        document.getElementById('click-user-filter').addEventListener('input', debouncedClickFilter);
        document.getElementById('click-partner-filter').addEventListener('input', debouncedClickFilter);
        document.getElementById('click-group-filter').addEventListener('change', debouncedClickFilter);

        // User filters
        document.getElementById('user-device-filter').addEventListener('change', debouncedUserFilter);
        document.getElementById('user-country-filter').addEventListener('input', debouncedUserFilter);

        // Ticket filters
        document.getElementById('ticket-status-filter').addEventListener('change', debouncedTicketFilter);
        document.getElementById('ticket-user-filter').addEventListener('input', debouncedTicketFilter);
    }

    switchSection(section) {
        // Update active menu item
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            searches: 'Search Management',
            clicks: 'Click Analytics',
            partners: 'Partner Analytics',
            users: 'User Management',
            tickets: 'Support Tickets',
            'affiliate-links': 'Affiliate Links'
        };
        document.getElementById('page-title').textContent = titles[section] || section;

        // Show/hide sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');

        this.currentSection = section;
        this.loadSection(section);
    }

    async loadSection(section) {
        try {
            switch (section) {
                case 'dashboard':
                    await this.loadDashboard();
                    break;
                case 'searches':
                    await this.loadSearches();
                    break;
                case 'clicks':
                    await this.loadClicks();
                    break;
                case 'partners':
                    await this.loadPartners();
                    break;
                case 'users':
                    await this.loadUsers();
                    break;
                case 'tickets':
                    await this.loadTickets();
                    break;
                case 'affiliate-links':
                    await this.loadAffiliateLinks();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${section}:`, error);
        }
    }

    async loadDashboard() {
        try {
            const data = await adminAPI.getDashboard(
                this.filters.dateRange.start,
                this.filters.dateRange.end
            );

            // Update stats
            document.getElementById('total-searches').textContent = Utils.formatNumber(data.total_searches);
            document.getElementById('total-clicks').textContent = Utils.formatNumber(data.total_clicks);
            document.getElementById('total-users').textContent = Utils.formatNumber(data.total_users);
            document.getElementById('ctr').textContent = Utils.formatPercentage(data.ctr);

            // Update charts
            if (data.seven_day_trend && data.seven_day_trend.length > 0) {
                chartManager.create7DayTrendChart(data.seven_day_trend);
            }

            if (data.thirty_day_trend && data.thirty_day_trend.length > 0) {
                chartManager.create30DayTrendChart(data.thirty_day_trend);
            }

            // Update top partners table
            this.updateTopPartnersTable(data.top_partners || []);

            // Update top sources table
            this.updateTopSourcesTable(data.top_sources || []);

        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    async loadTickets() {
        try {
            const filters = this.getTicketFilters();
            const data = await adminAPI.getTickets(this.currentPage.tickets, CONFIG.DEFAULT_PAGE_SIZE, filters);

            this.updateTicketsTable(data.tickets || []);
            this.updatePagination('tickets', data.page, data.total_pages);
            this.updateTicketBadge(data.tickets);

        } catch (error) {
            console.error('Error loading tickets:', error);
        }
    }

    getTicketFilters() {
        const filters = {};
        
        const status = document.getElementById('ticket-status-filter').value;
        if (status) filters.status = status;

        const userId = document.getElementById('ticket-user-filter').value;
        if (userId) filters.user_id = userId;

        if (this.filters.dateRange.start) filters.start_date = this.filters.dateRange.start;
        if (this.filters.dateRange.end) filters.end_date = this.filters.dateRange.end;

        return filters;
    }

    updateTicketsTable(tickets) {
        const tbody = document.querySelector('#tickets-table tbody');
        tbody.innerHTML = '';

        tickets.forEach(ticket => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${ticket.id}</td>
                <td>
                    <span class="text-sm font-mono">${Utils.truncateText(ticket.user_id, 8)}</span>
                </td>
                <td>${Utils.formatDate(ticket.created_at)}</td>
                <td>
                    <span class="status-badge status-${ticket.status}">
                        ${ticket.status}
                    </span>
                </td>
                <td>${Utils.truncateText(ticket.user_note, 50)}</td>
                <td>
                    ${ticket.crop_image_url ? 
                        `<img src="${ticket.crop_image_url}" class="image-preview" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" onclick="window.open('${ticket.crop_image_url}', '_blank')">` : 
                        'No image'
                    }
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="adminPanel.viewTicketDetail(${ticket.id})">
                        <i class="fas fa-eye"></i> View
                    </button>
                    ${ticket.status !== 'resolved' ? 
                        `<button class="btn btn-sm btn-success" onclick="adminPanel.resolveTicket(${ticket.id})">
                            <i class="fas fa-check"></i> Resolve
                        </button>` : ''
                    }
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async viewTicketDetail(ticketId) {
        try {
            const ticket = await adminAPI.getTicketDetail(ticketId);
            this.showTicketDetailModal(ticket);
        } catch (error) {
            console.error('Error loading ticket detail:', error);
        }
    }

    showTicketDetailModal(ticket) {
        const content = document.getElementById('ticket-detail-content');
        content.innerHTML = `
            <div class="ticket-detail">
                <div class="ticket-header">
                    <h4>Ticket #${ticket.id}</h4>
                    <span class="status-badge status-${ticket.status}">${ticket.status}</span>
                </div>
                
                <div class="ticket-info">
                    <div class="info-row">
                        <strong>User ID:</strong> ${ticket.user_id}
                    </div>
                    <div class="info-row">
                        <strong>Created:</strong> ${Utils.formatDate(ticket.created_at)}
                    </div>
                    <div class="info-row">
                        <strong>Last Updated:</strong> ${Utils.formatDate(ticket.updated_at)}
                    </div>
                    ${ticket.search_id ? `
                        <div class="info-row">
                            <strong>Related Search:</strong> #${ticket.search_id}
                        </div>
                    ` : ''}
                </div>

                <div class="ticket-content">
                    <h5>User Note:</h5>
                    <p class="user-note">${ticket.user_note}</p>
                </div>

                ${ticket.crop_image_url ? `
                    <div class="ticket-images">
                        <h5>Images:</h5>
                        <div class="image-gallery">
                            <img src="${ticket.crop_image_url}" alt="Crop Image" style="max-width: 200px; max-height: 200px; border-radius: 8px; cursor: pointer;" onclick="window.open('${ticket.crop_image_url}', '_blank')">
                            ${ticket.original_image_url ? `
                                <img src="${ticket.original_image_url}" alt="Original Image" style="max-width: 200px; max-height: 200px; border-radius: 8px; cursor: pointer;" onclick="window.open('${ticket.original_image_url}', '_blank')">
                            ` : ''}
                        </div>
                    </div>
                ` : ''}

                ${ticket.admin_notes ? `
                    <div class="admin-notes">
                        <h5>Admin Notes:</h5>
                        <p>${ticket.admin_notes}</p>
                    </div>
                ` : ''}

                ${ticket.status !== 'resolved' ? `
                    <div class="ticket-actions">
                        <h5>Actions:</h5>
                        <form id="ticket-update-form">
                            <div class="form-group">
                                <label for="ticket-status">Status:</label>
                                <select id="ticket-status" name="status">
                                    <option value="open" ${ticket.status === 'open' ? 'selected' : ''}>Open</option>
                                    <option value="in-progress" ${ticket.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
                                    <option value="resolved" ${ticket.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="admin-notes">Admin Notes:</label>
                                <textarea id="admin-notes" name="admin_notes" rows="3" placeholder="Add notes about the resolution...">${ticket.admin_notes || ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label for="resolved-by">Resolved By:</label>
                                <input type="text" id="resolved-by" name="resolved_by" value="${ticket.resolved_by || 'admin'}" placeholder="Admin username">
                            </div>
                            <div class="form-actions">
                                <button type="button" class="btn btn-secondary" onclick="adminPanel.closeModal('ticket-detail-modal')">Cancel</button>
                                <button type="submit" class="btn btn-primary">Update Ticket</button>
                            </div>
                        </form>
                    </div>
                ` : `
                    <div class="resolution-info">
                        <h5>Resolution Details:</h5>
                        <p><strong>Resolved By:</strong> ${ticket.resolved_by}</p>
                        <p><strong>Resolved At:</strong> ${Utils.formatDate(ticket.resolved_at)}</p>
                    </div>
                `}
            </div>
        `;

        // Setup form handler
        const form = document.getElementById('ticket-update-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updateTicketFromForm(ticket.id);
            });
        }

        this.openModal('ticket-detail-modal');
    }

    async updateTicketFromForm(ticketId) {
        try {
            const form = document.getElementById('ticket-update-form');
            const formData = new FormData(form);
            
            const updateData = {};
            for (let [key, value] of formData.entries()) {
                if (value.trim()) {
                    updateData[key] = value.trim();
                }
            }

            await adminAPI.updateTicket(ticketId, updateData);
            
            Utils.showNotification('Ticket updated successfully!', 'success');
            this.closeModal('ticket-detail-modal');
            this.loadTickets(); // Refresh the tickets list
            
        } catch (error) {
            console.error('Error updating ticket:', error);
            Utils.showNotification('Failed to update ticket', 'error');
        }
    }

    async resolveTicket(ticketId) {
        try {
            const updateData = {
                status: 'resolved',
                resolved_by: 'admin',
                admin_notes: 'Ticket resolved by admin'
            };

            await adminAPI.updateTicket(ticketId, updateData);
            
            Utils.showNotification('Ticket resolved successfully!', 'success');
            this.loadTickets(); // Refresh the tickets list
            
        } catch (error) {
            console.error('Error resolving ticket:', error);
            Utils.showNotification('Failed to resolve ticket', 'error');
        }
    }

    updateTicketBadge(tickets) {
        const openTickets = tickets.filter(ticket => ticket.status === 'open').length;
        const badge = document.getElementById('ticket-badge');
        badge.textContent = openTickets;
        badge.style.display = openTickets > 0 ? 'inline' : 'none';
    }

    updateTopPartnersTable(partners) {
        const tbody = document.querySelector('#top-partners-table tbody');
        tbody.innerHTML = '';

        partners.forEach(partner => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${partner.name}</td>
                <td>${Utils.formatNumber(partner.clicks)}</td>
                <td>${Utils.formatPercentage(partner.ctr)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updateTopSourcesTable(sources) {
        const tbody = document.querySelector('#top-sources-table tbody');
        tbody.innerHTML = '';

        sources.forEach(source => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${source.name}</td>
                <td>${Utils.formatNumber(source.searches)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePagination(section, currentPage, totalPages) {
        const pageInfo = document.getElementById(`${section}-page-info`);
        const prevBtn = document.getElementById(`${section}-prev`);
        const nextBtn = document.getElementById(`${section}-next`);

        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= totalPages;
    }

    applyDateFilter() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        this.filters.dateRange = { start: startDate, end: endDate };
        
        // Reload current section
        this.loadSection(this.currentSection);
        
        Utils.showNotification('Date filter applied', 'success');
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto';
    }

    startAutoRefresh() {
        if (!CONFIG.AUTO_REFRESH.enabled) return;

        // Dashboard auto-refresh
        autoRefresh.start('dashboard', () => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, CONFIG.AUTO_REFRESH.dashboard);

        // Tickets auto-refresh
        autoRefresh.start('tickets', () => {
            if (this.currentSection === 'tickets') {
                this.loadTickets();
            }
        }, CONFIG.AUTO_REFRESH.tickets);
    }

    // Placeholder methods for other sections
    async loadSearches() {
        // Implementation would be similar to loadTickets
        console.log('Loading searches...');
    }

    async loadClicks() {
        // Implementation would be similar to loadTickets
        console.log('Loading clicks...');
    }

    async loadPartners() {
        // Implementation would be similar to loadTickets
        console.log('Loading partners...');
    }

    async loadUsers() {
        // Implementation would be similar to loadTickets
        console.log('Loading users...');
    }

    async loadAffiliateLinks() {
        // Implementation would be similar to loadTickets
        console.log('Loading affiliate links...');
    }
}

// Initialize the admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        autoRefresh.stopAll();
    } else {
        adminPanel.startAutoRefresh();
    }
});

// Handle beforeunload
window.addEventListener('beforeunload', () => {
    autoRefresh.stopAll();
    chartManager.destroyAllCharts();
});