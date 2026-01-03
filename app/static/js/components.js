// Component JavaScript for ERP System

// Global Search Component
class GlobalSearch {
    constructor() {
        this.searchInput = document.getElementById('globalSearch');
        this.searchResults = document.getElementById('searchResults');
        this.searchModal = document.getElementById('globalSearchModal');
        this.searchModalInput = document.getElementById('globalSearchInput');
        this.searchSuggestions = document.getElementById('searchSuggestions');
        this.debounceTimer = null;
        this.currentResults = [];
        this.selectedIndex = -1;
        
        this.init();
    }

    init() {
        if (this.searchInput) {
            this.bindSearchEvents();
        }
        
        if (this.searchModal) {
            this.bindModalEvents();
        }
        
        this.bindKeyboardShortcuts();
    }

    bindSearchEvents() {
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        this.searchInput.addEventListener('focus', () => {
            if (this.searchInput.value.length > 0) {
                this.showResults();
            }
        });

        this.searchInput.addEventListener('blur', () => {
            // Delay hiding to allow clicking on results
            setTimeout(() => this.hideResults(), 200);
        });
    }

    bindModalEvents() {
        this.searchModalInput.addEventListener('input', (e) => {
            this.handleModalSearch(e.target.value);
        });

        this.searchModalInput.addEventListener('keydown', (e) => {
            this.handleModalKeydown(e);
        });

        // Show modal on Ctrl+K
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.showModal();
            }
        });
    }

    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Global search shortcut (Ctrl+K)
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                this.showModal();
            }
            
            // Focus search input (/)
            if (e.key === '/' && !this.isInputFocused()) {
                e.preventDefault();
                this.searchInput?.focus();
            }
        });
    }

    handleSearch(query) {
        clearTimeout(this.debounceTimer);
        
        if (query.length < 2) {
            this.hideResults();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    handleModalSearch(query) {
        clearTimeout(this.debounceTimer);
        
        if (query.length < 2) {
            this.clearModalResults();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.performModalSearch(query);
        }, 300);
    }

    handleModalKeydown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateResults(1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateResults(-1);
                break;
            case 'Enter':
                e.preventDefault();
                this.selectResult();
                break;
            case 'Escape':
                this.hideModal();
                break;
        }
    }

    async performSearch(query) {
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query })
            });

            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    async performModalSearch(query) {
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ query, detailed: true })
            });

            if (response.ok) {
                const results = await response.json();
                this.displayModalResults(results);
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    displayResults(results) {
        if (!this.searchResults) return;

        this.currentResults = results;
        
        if (results.length === 0) {
            this.searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            this.searchResults.innerHTML = results.map(result => `
                <div class="search-result-item" data-url="${result.url}">
                    <div class="search-result-icon">
                        <i class="${result.icon}"></i>
                    </div>
                    <div class="search-result-content">
                        <div class="search-result-title">${result.title}</div>
                        <div class="search-result-description">${result.description}</div>
                    </div>
                </div>
            `).join('');
        }

        this.showResults();
        this.bindResultEvents();
    }

    displayModalResults(results) {
        if (!this.searchSuggestions) return;

        this.currentResults = results;
        this.selectedIndex = -1;
        
        if (results.length === 0) {
            this.searchSuggestions.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            this.searchSuggestions.innerHTML = results.map((result, index) => `
                <div class="search-suggestion-item ${index === this.selectedIndex ? 'selected' : ''}" 
                     data-index="${index}" data-url="${result.url}">
                    <div class="search-suggestion-icon">
                        <i class="${result.icon}"></i>
                    </div>
                    <div class="search-suggestion-content">
                        <div class="search-suggestion-title">${result.title}</div>
                        <div class="search-suggestion-description">${result.description}</div>
                        <div class="search-suggestion-category">${result.category}</div>
                    </div>
                </div>
            `).join('');
        }

        this.bindModalResultEvents();
    }

    bindResultEvents() {
        const resultItems = this.searchResults.querySelectorAll('.search-result-item');
        resultItems.forEach(item => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            });
        });
    }

    bindModalResultEvents() {
        const suggestionItems = this.searchSuggestions.querySelectorAll('.search-suggestion-item');
        suggestionItems.forEach(item => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                if (url) {
                    this.hideModal();
                    window.location.href = url;
                }
            });
        });
    }

    navigateResults(direction) {
        if (this.currentResults.length === 0) return;

        this.selectedIndex += direction;
        
        if (this.selectedIndex < 0) {
            this.selectedIndex = this.currentResults.length - 1;
        } else if (this.selectedIndex >= this.currentResults.length) {
            this.selectedIndex = 0;
        }

        this.updateSelectedResult();
    }

    updateSelectedResult() {
        const items = this.searchSuggestions.querySelectorAll('.search-suggestion-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
        });
    }

    selectResult() {
        if (this.selectedIndex >= 0 && this.currentResults[this.selectedIndex]) {
            const result = this.currentResults[this.selectedIndex];
            this.hideModal();
            window.location.href = result.url;
        }
    }

    showResults() {
        if (this.searchResults) {
            this.searchResults.style.display = 'block';
        }
    }

    hideResults() {
        if (this.searchResults) {
            this.searchResults.style.display = 'none';
        }
    }

    showModal() {
        if (this.searchModal) {
            const modal = new bootstrap.Modal(this.searchModal);
            modal.show();
            setTimeout(() => {
                this.searchModalInput?.focus();
            }, 300);
        }
    }

    hideModal() {
        if (this.searchModal) {
            const modal = bootstrap.Modal.getInstance(this.searchModal);
            if (modal) {
                modal.hide();
            }
        }
    }

    clearModalResults() {
        if (this.searchSuggestions) {
            this.searchSuggestions.innerHTML = '';
        }
        this.currentResults = [];
        this.selectedIndex = -1;
    }

    isInputFocused() {
        const activeElement = document.activeElement;
        return activeElement && (
            activeElement.tagName === 'INPUT' || 
            activeElement.tagName === 'TEXTAREA' || 
            activeElement.contentEditable === 'true'
        );
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Sidebar Component
class SidebarManager {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebarClose = document.getElementById('sidebarClose');
        this.mobileOverlay = document.getElementById('mobileOverlay');
        this.mainContent = document.getElementById('mainContent');
        
        this.isCollapsed = this.getStoredState();
        this.isMobile = window.innerWidth <= 768;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateSidebarState();
        this.initializeSubmenuStates();
    }

    bindEvents() {
        // Toggle button
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => {
                this.toggle();
            });
        }

        // Close button (mobile)
        if (this.sidebarClose) {
            this.sidebarClose.addEventListener('click', () => {
                this.hide();
            });
        }

        // Mobile overlay
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => {
                this.hide();
            });
        }

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Keyboard shortcut (Ctrl+/)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                this.toggle();
            }
        });

        // Submenu toggles
        this.bindSubmenuEvents();
    }

    bindSubmenuEvents() {
        const submenuToggles = document.querySelectorAll('.nav-link.has-submenu');
        submenuToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSubmenu(toggle);
            });
        });
    }

    toggleSubmenu(toggle) {
        const submenuId = toggle.getAttribute('data-submenu');
        const submenu = document.getElementById(submenuId);
        
        if (!submenu) return;

        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        
        // Toggle current submenu
        toggle.setAttribute('aria-expanded', (!isExpanded).toString());
        submenu.classList.toggle('show', !isExpanded);
        
        // Store submenu state
        this.storeSubmenuState(submenuId, !isExpanded);
    }

    initializeSubmenuStates() {
        const submenuStates = this.getStoredSubmenuStates();
        
        Object.keys(submenuStates).forEach(submenuId => {
            const submenu = document.getElementById(submenuId);
            const toggle = document.querySelector(`[data-submenu="${submenuId}"]`);
            
            if (submenu && toggle && submenuStates[submenuId]) {
                toggle.setAttribute('aria-expanded', 'true');
                submenu.classList.add('show');
            }
        });
    }

    toggle() {
        if (this.isMobile) {
            this.sidebar?.classList.toggle('show');
            this.mobileOverlay?.classList.toggle('show');
        } else {
            this.isCollapsed = !this.isCollapsed;
            this.updateSidebarState();
            this.storeState();
        }
    }

    show() {
        if (this.isMobile) {
            this.sidebar?.classList.add('show');
            this.mobileOverlay?.classList.add('show');
        } else {
            this.isCollapsed = false;
            this.updateSidebarState();
            this.storeState();
        }
    }

    hide() {
        if (this.isMobile) {
            this.sidebar?.classList.remove('show');
            this.mobileOverlay?.classList.remove('show');
        } else {
            this.isCollapsed = true;
            this.updateSidebarState();
            this.storeState();
        }
    }

    updateSidebarState() {
        if (!this.isMobile) {
            this.sidebar?.classList.toggle('collapsed', this.isCollapsed);
            this.mainContent?.classList.toggle('sidebar-collapsed', this.isCollapsed);
        }
    }

    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            // Reset states when switching between mobile/desktop
            this.sidebar?.classList.remove('show', 'collapsed');
            this.mobileOverlay?.classList.remove('show');
            this.mainContent?.classList.remove('sidebar-collapsed');
            
            if (!this.isMobile) {
                this.updateSidebarState();
            }
        }
    }

    getStoredState() {
        return localStorage.getItem('sidebarCollapsed') === 'true';
    }

    storeState() {
        localStorage.setItem('sidebarCollapsed', this.isCollapsed.toString());
    }

    getStoredSubmenuStates() {
        const stored = localStorage.getItem('submenuStates');
        return stored ? JSON.parse(stored) : {};
    }

    storeSubmenuState(submenuId, isOpen) {
        const states = this.getStoredSubmenuStates();
        states[submenuId] = isOpen;
        localStorage.setItem('submenuStates', JSON.stringify(states));
    }
}

// Notification Manager
class NotificationManager {
    constructor() {
        this.container = document.querySelector('.toast-container');
        this.notificationBtn = document.querySelector('.notification-btn');
        this.notificationBadge = document.querySelector('.notification-badge');
        this.notifications = [];
        this.unreadCount = 0;
        
        this.init();
    }

    init() {
        this.loadNotifications();
        this.bindEvents();
        this.startPolling();
    }

    bindEvents() {
        // Mark all as read
        const markAllReadBtn = document.querySelector('[data-action="mark-all-read"]');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (response.ok) {
                const data = await response.json();
                this.notifications = data.notifications || [];
                this.unreadCount = data.unread_count || 0;
                this.updateBadge();
            } else {
                console.warn('Notifications API not available');
                // Use mock data if API is not available
                this.notifications = [];
                this.unreadCount = 0;
                this.updateBadge();
            }
        } catch (error) {
            console.warn('Failed to load notifications:', error);
            // Use mock data if API fails
            this.notifications = [];
            this.unreadCount = 0;
            this.updateBadge();
        }
    }

    startPolling() {
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.loadNotifications();
        }, 30000);
    }

    showToast(message, type = 'info', duration = 5000) {
        const toastId = 'toast-' + Date.now();
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${iconMap[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        this.container?.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });

        bsToast.show();

        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        return toastId;
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                this.unreadCount = 0;
                this.updateBadge();
                this.showToast('All notifications marked as read', 'success');
            }
        } catch (error) {
            console.error('Failed to mark notifications as read:', error);
            this.showToast('Failed to mark notifications as read', 'error');
        }
    }

    updateBadge() {
        if (this.notificationBadge) {
            if (this.unreadCount > 0) {
                this.notificationBadge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                this.notificationBadge.style.display = 'flex';
            } else {
                this.notificationBadge.style.display = 'none';
            }
        }
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Scroll to Top Component
class ScrollToTop {
    constructor() {
        this.button = document.getElementById('scrollToTop');
        this.threshold = 300;
        
        this.init();
    }

    init() {
        if (!this.button) {
            this.createButton();
        }
        
        this.bindEvents();
        this.handleScroll();
    }

    createButton() {
        // Create scroll to top button if it doesn't exist
        this.button = document.createElement('button');
        this.button.id = 'scrollToTop';
        this.button.className = 'scroll-to-top';
        this.button.innerHTML = '<i class="fas fa-chevron-up"></i>';
        this.button.title = 'Scroll to top';
        this.button.setAttribute('aria-label', 'Scroll to top');
        
        document.body.appendChild(this.button);
    }

    bindEvents() {
        window.addEventListener('scroll', () => {
            this.handleScroll();
        });

        this.button.addEventListener('click', () => {
            this.scrollToTop();
        });
    }

    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > this.threshold) {
            this.button.classList.add('show');
        } else {
            this.button.classList.remove('show');
        }
    }

    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// Form Enhancement Component
class FormEnhancer {
    constructor() {
        this.forms = document.querySelectorAll('form');
        this.init();
    }

    init() {
        this.enhanceForms();
        this.bindGlobalEvents();
    }

    enhanceForms() {
        this.forms.forEach(form => {
            this.enhanceForm(form);
        });
    }

    enhanceForm(form) {
        // Add loading states to submit buttons
        const submitBtns = form.querySelectorAll('button[type="submit"], input[type="submit"]');
        submitBtns.forEach(btn => {
            form.addEventListener('submit', () => {
                this.setButtonLoading(btn);
            });
        });

        // Auto-save functionality
        if (form.hasAttribute('data-auto-save')) {
            this.enableAutoSave(form);
        }

        // Real-time validation
        if (form.hasAttribute('data-live-validation')) {
            this.enableLiveValidation(form);
        }
    }

    setButtonLoading(button) {
        const originalText = button.textContent;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        button.disabled = true;
    }

    resetButtonLoading(button) {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.textContent = originalText;
            button.disabled = false;
        }
    }

    enableAutoSave(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let saveTimeout;

        inputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    this.autoSave(form);
                }, 2000);
            });
        });
    }

    async autoSave(form) {
        const url = form.getAttribute('data-auto-save-url');
        if (!url) return;

        try {
            const formData = new FormData(form);
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                this.showAutoSaveIndicator('saved');
            } else {
                this.showAutoSaveIndicator('error');
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
            this.showAutoSaveIndicator('error');
        }
    }

    showAutoSaveIndicator(status) {
        // Create or update auto-save indicator
        let indicator = document.getElementById('auto-save-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'auto-save-indicator';
            indicator.className = 'auto-save-indicator';
            document.body.appendChild(indicator);
        }

        const messages = {
            saving: '<i class="fas fa-spinner fa-spin"></i> Saving...',
            saved: '<i class="fas fa-check"></i> Saved',
            error: '<i class="fas fa-exclamation-triangle"></i> Save failed'
        };

        indicator.innerHTML = messages[status];
        indicator.className = `auto-save-indicator ${status}`;
        indicator.style.display = 'block';

        if (status !== 'saving') {
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }

    enableLiveValidation(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });
    }

    validateField(field) {
        const isValid = field.checkValidity();
        const feedback = field.parentNode.querySelector('.invalid-feedback');
        
        field.classList.toggle('is-valid', isValid);
        field.classList.toggle('is-invalid', !isValid);
        
        if (!isValid && feedback) {
            feedback.textContent = field.validationMessage;
        }
    }

    bindGlobalEvents() {
        // Prevent double submission
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-submitted')) {
                e.preventDefault();
                return false;
            }
            form.setAttribute('data-submitted', 'true');
        });

        // Reset form state on page load
        window.addEventListener('pageshow', () => {
            this.forms.forEach(form => {
                form.removeAttribute('data-submitted');
                const submitBtns = form.querySelectorAll('button[type="submit"], input[type="submit"]');
                submitBtns.forEach(btn => {
                    this.resetButtonLoading(btn);
                });
            });
        });
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Initialize all components
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    window.globalSearch = new GlobalSearch();
    window.sidebarManager = new SidebarManager();
    window.notificationManager = new NotificationManager();
    window.scrollToTop = new ScrollToTop();
    window.formEnhancer = new FormEnhancer();
    
    console.log('ERP Components initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        GlobalSearch,
        SidebarManager,
        NotificationManager,
        ScrollToTop,
        FormEnhancer
    };
}
