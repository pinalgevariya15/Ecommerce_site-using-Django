/* custom_admin.js */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initSidebar();
    injectNavIcons();
    initProfileDropdown();
    initNavFilter();
    initDashboardStats();
    initMobileResponsiveTables();
    initGlobalSearch();
});

/* ==========================================================================
   1. COLLAPSIBLE SIDEBAR
   ========================================================================== */
function initSidebar() {
    const sidebar = document.getElementById('nav-sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (!toggleBtn || !sidebar) return;

    // Check saved state
    const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
    if (isCollapsed && window.innerWidth > 768) {
        document.body.classList.add('sidebar-collapsed');
    }

    toggleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (window.innerWidth <= 768) {
            // Mobile toggle behavior
            document.body.classList.toggle('sidebar-open');
        } else {
            // Desktop collapse behavior
            document.body.classList.toggle('sidebar-collapsed');
            const collapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar_collapsed', collapsed);
        }
    });

    // Close sidebar on mobile when clicking content area
    const content = document.getElementById('content');
    if (content) {
        content.addEventListener('click', function() {
            if (window.innerWidth <= 768 && document.body.classList.contains('sidebar-open')) {
                document.body.classList.remove('sidebar-open');
            }
        });
    }
}

/* ==========================================================================
   2. APP & MODEL SVG ICONS INJECTOR
   ========================================================================== */
function injectNavIcons() {
    // Mapping of model names (lowercase) to SVG icon paths
    const iconPaths = {
        'dashboard': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>`,
        'category': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`,
        'product': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
        'productimage': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>`,
        'cart': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>`,
        'cartitem': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>`,
        'order': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>`,
        'orderitem': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>`,
        'review': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
        'wishlist': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>`,
        'wishlistitem': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path></svg>`,
        'userprofile': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
        'coupon': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>`,
        'user': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
        'group': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
        'logentry': `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>`
    };

    const iconContainers = document.querySelectorAll('[data-model-icon]');
    iconContainers.forEach(container => {
        const modelName = container.getAttribute('data-model-icon').toLowerCase();
        if (iconPaths[modelName]) {
            container.innerHTML = iconPaths[modelName];
        }
    });
}

/* ==========================================================================
   3. USER PROFILE DROPDOWN MENU
   ========================================================================== */
function initProfileDropdown() {
    const trigger = document.querySelector('.user-profile-menu');
    const menu = document.querySelector('.user-dropdown-menu');
    if (!trigger || !menu) return;

    trigger.addEventListener('click', function(e) {
        e.stopPropagation();
        menu.classList.toggle('show');
    });

    document.addEventListener('click', function(e) {
        if (!trigger.contains(e.target)) {
            menu.classList.remove('show');
        }
    });
}

/* ==========================================================================
   4. SIDEBAR NAVIGATION FILTER SEARCH
   ========================================================================== */
function initNavFilter() {
    const filterInput = document.getElementById('nav-filter');
    if (!filterInput) return;

    filterInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        const appWrappers = document.querySelectorAll('.nav-section-wrapper');

        appWrappers.forEach(wrapper => {
            let visibleItemsCount = 0;
            const items = wrapper.querySelectorAll('.nav-item');
            
            // Skip the static dashboard section wrapper if it's the first wrapper
            if (wrapper.querySelector('[data-model="dashboard"]')) {
                return; 
            }

            items.forEach(item => {
                const text = item.querySelector('.nav-text').textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = '';
                    visibleItemsCount++;
                } else {
                    item.style.display = 'none';
                }
            });

            // Hide the application section completely if no child models are visible
            if (visibleItemsCount === 0 && query !== '') {
                wrapper.style.display = 'none';
            } else {
                wrapper.style.display = '';
            }
        });
    });
}

/* ==========================================================================
   5. ASYNCHRONOUS METRICS PARSING FOR THE DASHBOARD
   ========================================================================== */
function initDashboardStats() {
    const revenueCard = document.getElementById('metric-revenue');
    if (!revenueCard) return; // Only execute this script on the main dashboard page

    // Config mappings for dashboard fetch endpoints
    const statsConfig = [
        {
            url: '/admin/store/order/',
            countSelector: '#val-orders',
            subSelector: '#val-orders-sub',
            successMessage: 'Order entries',
            processResponse: (doc) => {
                // Also compute total revenue volume from order rows on first page
                const revenueElement = document.getElementById('val-revenue');
                if (revenueElement) {
                    const priceCells = doc.querySelectorAll('.field-total_amount');
                    let revenueSum = 0;
                    priceCells.forEach(cell => {
                        // Strip currency, spaces and parse value
                        const val = parseFloat(cell.textContent.replace(/[^\d.]/g, ''));
                        if (!isNaN(val)) {
                            revenueSum += val;
                        }
                    });
                    revenueElement.textContent = '₹' + revenueSum.toLocaleString('en-IN', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    });
                    revenueElement.classList.remove('shimmer');
                }
            }
        },
        {
            url: '/admin/store/product/',
            countSelector: '#val-products',
            subSelector: '#val-products-sub',
            successMessage: 'Active items'
        },
        {
            url: '/admin/store/review/',
            countSelector: '#val-reviews',
            subSelector: '#val-reviews-sub',
            successMessage: 'Submitted reviews'
        }
    ];

    // Fetch and populate metrics in background
    statsConfig.forEach(config => {
        fetch(config.url)
            .then(res => {
                if (!res.ok) throw new Error('Network error');
                return res.text();
            })
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const count = parseCount(doc);
                
                // Set the counter value
                const countEl = document.querySelector(config.countSelector);
                if (countEl) {
                    countEl.textContent = count.toLocaleString();
                    countEl.classList.remove('shimmer');
                }

                // Set sub-caption indicators
                const subEl = document.querySelector(config.subSelector);
                if (subEl) {
                    subEl.className = 'metric-trend success';
                    subEl.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> <span>${config.successMessage}</span>`;
                }

                // Perform extra processing if required
                if (config.processResponse) {
                    config.processResponse(doc);
                }
            })
            .catch(err => {
                console.error('Failed to fetch admin stat metrics for ' + config.url, err);
                
                const countEl = document.querySelector(config.countSelector);
                if (countEl) {
                    countEl.textContent = '0';
                    countEl.classList.remove('shimmer');
                }

                const subEl = document.querySelector(config.subSelector);
                if (subEl) {
                    subEl.className = 'metric-trend warning';
                    subEl.textContent = 'Offline placeholder';
                }
                
                // Fallback for revenue if fetch fails
                if (config.url === '/admin/store/order/') {
                    const revEl = document.getElementById('val-revenue');
                    if (revEl) {
                        revEl.textContent = '₹0.00';
                        revEl.classList.remove('shimmer');
                    }
                }
            });
    });
}

function parseCount(doc) {
    // 1. Attempt to find count inside pagination text container
    const paginator = doc.querySelector('.paginator');
    if (paginator) {
        const text = paginator.textContent.trim();
        // Regex extracts digits followed by words or digits alone
        const matches = text.match(/(\d+)\s+(total|result|item|order|product|coupon|review|user|profile|cart|categories|entries)/i) 
                     || text.match(/(\d+)\s+[\w\s]+$/)
                     || text.match(/(\d+)/);
        if (matches && matches[1]) {
            return parseInt(matches[1], 10);
        }
    }
    
    // 2. Count row entries directly inside changelist list tables if paginator text is missing
    const tableRows = doc.querySelectorAll('#result_list tbody tr');
    if (tableRows.length > 0) {
        const firstRow = tableRows[0];
        // Handle empty table states (often labeled with a class or contains text indicating no results)
        if (tableRows.length === 1 && (firstRow.classList.contains('empty') || firstRow.textContent.toLowerCase().includes('no') || firstRow.textContent.toLowerCase().includes('0'))) {
            return 0;
        }
        return tableRows.length;
    }
    
    return 0;
}

/* ==========================================================================
   6. RESPONSIVE UTILITIES FOR TABLES
   ========================================================================== */
function initMobileResponsiveTables() {
    const resultListTable = document.querySelector('#changelist form table');
    if (resultListTable) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive-wrapper';
        
        // Wrap table inside responsive scroll wrapper
        resultListTable.parentNode.insertBefore(wrapper, resultListTable);
        wrapper.appendChild(resultListTable);
    }
}

/* ==========================================================================
   7. GLOBAL SEARCH ROUTING
   ========================================================================== */
function initGlobalSearch() {
    const searchInput = document.getElementById('global-search-input');
    if (!searchInput) return;

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = this.value.trim();
            if (!query) return;

            // Smart redirection based on search pattern
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const orderRegex = /^(ord|order)/i;
            
            if (emailRegex.test(query)) {
                window.location.href = `/admin/store/userprofile/?q=${encodeURIComponent(query)}`;
            } else if (orderRegex.test(query) || (/^\d+$/.test(query) && query.length >= 4)) {
                window.location.href = `/admin/store/order/?q=${encodeURIComponent(query)}`;
            } else {
                window.location.href = `/admin/store/product/?q=${encodeURIComponent(query)}`;
            }
        }
    });
}
