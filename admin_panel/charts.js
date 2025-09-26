// Charts functionality for Admin Panel
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            }
        };
    }

    // Create or update a chart
    createChart(canvasId, type, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas with id '${canvasId}' not found`);
            return null;
        }

        // Destroy existing chart if it exists
        if (this.charts.has(canvasId)) {
            this.charts.get(canvasId).destroy();
        }

        const ctx = canvas.getContext('2d');
        const mergedOptions = this.mergeOptions(this.defaultOptions, options);

        const chart = new Chart(ctx, {
            type,
            data,
            options: mergedOptions
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    // Update existing chart data
    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    // Destroy a chart
    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    // Destroy all charts
    destroyAllCharts() {
        this.charts.forEach((chart) => {
            chart.destroy();
        });
        this.charts.clear();
    }

    // Merge options recursively
    mergeOptions(defaultOptions, customOptions) {
        const merged = JSON.parse(JSON.stringify(defaultOptions));
        
        function merge(target, source) {
            for (const key in source) {
                if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                    target[key] = target[key] || {};
                    merge(target[key], source[key]);
                } else {
                    target[key] = source[key];
                }
            }
        }
        
        merge(merged, customOptions);
        return merged;
    }

    // Create 7-day trend chart
    create7DayTrendChart(data) {
        const chartData = {
            labels: data.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }),
            datasets: [
                {
                    label: 'Searches',
                    data: data.map(item => item.searches),
                    borderColor: CONFIG.CHART_COLORS.primary,
                    backgroundColor: CONFIG.CHART_COLORS.primary + '20',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Clicks',
                    data: data.map(item => item.clicks),
                    borderColor: CONFIG.CHART_COLORS.success,
                    backgroundColor: CONFIG.CHART_COLORS.success + '20',
                    fill: true,
                    tension: 0.4
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Last 7 Days Activity'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        };

        return this.createChart('seven-day-chart', 'line', chartData, options);
    }

    // Create 30-day trend chart
    create30DayTrendChart(data) {
        const chartData = {
            labels: data.map(item => item.week),
            datasets: [
                {
                    label: 'Searches',
                    data: data.map(item => item.searches),
                    backgroundColor: CONFIG.CHART_COLORS.primary,
                    borderColor: CONFIG.CHART_COLORS.primary,
                    borderWidth: 2
                },
                {
                    label: 'Clicks',
                    data: data.map(item => item.clicks),
                    backgroundColor: CONFIG.CHART_COLORS.success,
                    borderColor: CONFIG.CHART_COLORS.success,
                    borderWidth: 2
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Last 30 Days Weekly Trend'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        };

        return this.createChart('thirty-day-chart', 'bar', chartData, options);
    }

    // Create partner performance chart
    createPartnerChart(data) {
        const sortedData = data.sort((a, b) => b.clicks - a.clicks).slice(0, 10);
        
        const chartData = {
            labels: sortedData.map(item => item.name),
            datasets: [
                {
                    label: 'Clicks',
                    data: sortedData.map(item => item.clicks),
                    backgroundColor: [
                        CONFIG.CHART_COLORS.primary,
                        CONFIG.CHART_COLORS.success,
                        CONFIG.CHART_COLORS.warning,
                        CONFIG.CHART_COLORS.danger,
                        CONFIG.CHART_COLORS.info,
                        '#8b5cf6',
                        '#f59e0b',
                        '#10b981',
                        '#ef4444',
                        '#6366f1'
                    ]
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Partners by Clicks'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Clicks'
                    }
                }
            }
        };

        return this.createChart('partner-chart', 'bar', chartData, options);
    }

    // Create user activity chart
    createUserActivityChart(data) {
        const chartData = {
            labels: ['Active Today', 'Active This Week', 'Active This Month', 'Inactive'],
            datasets: [
                {
                    data: [
                        data.activeToday || 0,
                        data.activeThisWeek || 0,
                        data.activeThisMonth || 0,
                        data.inactive || 0
                    ],
                    backgroundColor: [
                        CONFIG.CHART_COLORS.success,
                        CONFIG.CHART_COLORS.primary,
                        CONFIG.CHART_COLORS.warning,
                        CONFIG.CHART_COLORS.danger
                    ]
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'User Activity Distribution'
                }
            }
        };

        return this.createChart('user-activity-chart', 'doughnut', chartData, options);
    }

    // Create device distribution chart
    createDeviceChart(data) {
        const chartData = {
            labels: data.map(item => item.device_type),
            datasets: [
                {
                    data: data.map(item => item.count),
                    backgroundColor: [
                        CONFIG.CHART_COLORS.primary,
                        CONFIG.CHART_COLORS.success,
                        CONFIG.CHART_COLORS.warning
                    ]
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Device Distribution'
                }
            }
        };

        return this.createChart('device-chart', 'pie', chartData, options);
    }

    // Create search success rate chart
    createSearchSuccessChart(data) {
        const chartData = {
            labels: data.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }),
            datasets: [
                {
                    label: 'Success Rate (%)',
                    data: data.map(item => item.successRate),
                    borderColor: CONFIG.CHART_COLORS.success,
                    backgroundColor: CONFIG.CHART_COLORS.success + '20',
                    fill: true,
                    tension: 0.4
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Search Success Rate Trend'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Success Rate (%)'
                    }
                }
            }
        };

        return this.createChart('search-success-chart', 'line', chartData, options);
    }

    // Create ticket resolution chart
    createTicketResolutionChart(data) {
        const chartData = {
            labels: ['Open', 'In Progress', 'Resolved'],
            datasets: [
                {
                    data: [
                        data.open || 0,
                        data.inProgress || 0,
                        data.resolved || 0
                    ],
                    backgroundColor: [
                        CONFIG.STATUS_COLORS.open,
                        CONFIG.STATUS_COLORS['in-progress'],
                        CONFIG.STATUS_COLORS.resolved
                    ]
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Ticket Status Distribution'
                }
            }
        };

        return this.createChart('ticket-resolution-chart', 'doughnut', chartData, options);
    }

    // Create revenue chart (if revenue data is available)
    createRevenueChart(data) {
        const chartData = {
            labels: data.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }),
            datasets: [
                {
                    label: 'Revenue ($)',
                    data: data.map(item => item.revenue),
                    borderColor: CONFIG.CHART_COLORS.success,
                    backgroundColor: CONFIG.CHART_COLORS.success + '20',
                    fill: true,
                    tension: 0.4
                }
            ]
        };

        const options = {
            plugins: {
                title: {
                    display: true,
                    text: 'Revenue Trend'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        };

        return this.createChart('revenue-chart', 'line', chartData, options);
    }

    // Resize all charts (useful for responsive design)
    resizeAllCharts() {
        this.charts.forEach((chart) => {
            chart.resize();
        });
    }

    // Export chart as image
    exportChart(canvasId, filename = 'chart.png') {
        const chart = this.charts.get(canvasId);
        if (chart) {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
        }
    }

    // Get chart data for export
    getChartData(canvasId) {
        const chart = this.charts.get(canvasId);
        return chart ? chart.data : null;
    }
}

// Create global chart manager instance
window.chartManager = new ChartManager();

// Handle window resize
window.addEventListener('resize', Utils.debounce(() => {
    chartManager.resizeAllCharts();
}, 250));

// Chart themes
const ChartThemes = {
    light: {
        backgroundColor: '#ffffff',
        textColor: '#374151',
        gridColor: 'rgba(0, 0, 0, 0.1)',
        borderColor: 'rgba(0, 0, 0, 0.2)'
    },
    dark: {
        backgroundColor: '#1f2937',
        textColor: '#f9fafb',
        gridColor: 'rgba(255, 255, 255, 0.1)',
        borderColor: 'rgba(255, 255, 255, 0.2)'
    }
};

// Apply theme to charts
function applyChartTheme(theme = 'light') {
    const themeConfig = ChartThemes[theme];
    
    Chart.defaults.color = themeConfig.textColor;
    Chart.defaults.borderColor = themeConfig.borderColor;
    Chart.defaults.backgroundColor = themeConfig.backgroundColor;
    
    // Update existing charts
    chartManager.charts.forEach((chart) => {
        chart.options.scales.x.grid.color = themeConfig.gridColor;
        chart.options.scales.y.grid.color = themeConfig.gridColor;
        chart.update();
    });
}

// Auto-detect and apply theme based on system preference
function detectAndApplyTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyChartTheme(prefersDark ? 'dark' : 'light');
}

// Listen for theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', detectAndApplyTheme);

// Initialize theme
detectAndApplyTheme();