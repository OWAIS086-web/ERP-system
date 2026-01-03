// Keyboard Shortcuts for ERP System

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.modal = document.getElementById('shortcutsModal');
        this.isEnabled = true;
        this.init();
    }

    init() {
        this.registerDefaultShortcuts();
        this.bindEvents();
        this.loadUserShortcuts();
    }

    registerDefaultShortcuts() {
        // Navigation shortcuts
        this.register('ctrl+h', () => {
            window.location.href = '/dashboard';
        }, 'Go to Dashboard', 'Navigation');

        this.register('ctrl+/', () => {
            window.sidebarManager?.toggle();
        }, 'Toggle Sidebar', 'Navigation');

        this.register('ctrl+k', () => {
            window.globalSearch?.showModal();
        }, 'Global Search', 'Navigation');

        this.register('escape', () => {
            this.closeModals();
        }, 'Close Modals', 'Navigation');

        // Action shortcuts
        this.register('ctrl+n', () => {
            this.handleNewRecord();
        }, 'New Record', 'Actions');

        this.register('ctrl+s', (e) => {
            e.preventDefault();
            this.handleSave();
        }, 'Save', 'Actions');

        this.register('ctrl+e', () => {
            this.handleEdit();
        }, 'Edit', 'Actions');

        this.register('ctrl+d', (e) => {
            e.preventDefault();
            this.handleDelete();
        }, 'Delete', 'Actions');

        // Theme shortcuts
        this.register('ctrl+shift+t', () => {
            window.themeManager?.toggleTheme();
        }, 'Toggle Theme', 'Theme');

        // Help shortcuts
        this.register('?', () => {
            this.showShortcutsModal();
        }, 'Show Shortcuts', 'Help');

        this.register('f1', (e) => {
            e.preventDefault();
            this.showHelp();
        }, 'Show Help', 'Help');

        // Quick actions
        this.register('alt+c', () => {
            this.navigateToModule('sales', 'add_customer');
        }, 'New Customer', 'Quick Actions');

        this.register('alt+o', () => {
            this.navigateToModule('sales', 'add_order');
        }, 'New Order', 'Quick Actions');

        this.register('alt+p', () => {
            this.navigateToModule('inventory', 'add_product');
        }, 'New Product', 'Quick Actions');

        this.register('alt+e', () => {
            this.navigateToModule('hr', 'add_employee');
        }, 'New Employee', 'Quick Actions');

        this.register('alt+i', () => {
            this.navigateToModule('finance', 'create_invoice');
        }, 'New Invoice', 'Quick Actions');

        // Module navigation
        this.register('ctrl+1', () => {
            window.location.href = '/dashboard';
        }, 'Dashboard', 'Modules');

        this.register('ctrl+2', () => {
            window.location.href = '/sales';
        }, 'Sales Module', 'Modules');

        this.register('ctrl+3', () => {
            window.location.href = '/inventory';
        }, 'Inventory Module', 'Modules');

        this.register('ctrl+4', () => {
            window.location.href = '/finance';
        }, 'Finance Module', 'Modules');

        this.register('ctrl+5', () => {
            window.location.href = '/hr';
        }, 'HR Module', 'Modules');

        this.register('ctrl+6', () => {
            window.location.href = '/procurement';
        }, 'Procurement Module', 'Modules');

        this.register('ctrl+7', () => {
            window.location.href = '/projects';
        }, 'Projects Module', 'Modules');

        this.register('ctrl+8', () => {
            window.location.href = '/reports';
        }, 'Reports Module', 'Modules');
    }

    register(combination, callback, description, category = 'General') {
        const key = this.normalizeKey(combination);
        this.shortcuts.set(key, {
            callback,
            description,
            category,
            combination: combination.toUpperCase()
        });
    }

    unregister(combination) {
        const key = this.normalizeKey(combination);
        this.shortcuts.delete(key);
    }

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (!this.isEnabled) return;
            
            // Don't trigger shortcuts when typing in inputs
            if (this.isInputFocused() && !this.isGlobalShortcut(e)) {
                return;
            }

            const key = this.getKeyFromEvent(e);
            const shortcut = this.shortcuts.get(key);

            if (shortcut) {
                try {
                    shortcut.callback(e);
                    this.logShortcutUsage(key);
                } catch (error) {
                    console.error('Shortcut execution error:', error);
                }
            }
        });

        // Show shortcuts modal on ? key
        document.addEventListener('keypress', (e) => {
            if (e.key === '?' && !this.isInputFocused()) {
                e.preventDefault();
                this.showShortcutsModal();
            }
        });
    }

    normalizeKey(combination) {
        return combination.toLowerCase()
            .replace(/\s+/g, '')
            .split('+')
            .sort()
            .join('+');
    }

    getKeyFromEvent(e) {
        const parts = [];
        
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        if (e.metaKey) parts.push('meta');
        
        const key = e.key.toLowerCase();
        if (key !== 'control' && key !== 'alt' && key !== 'shift' && key !== 'meta') {
            parts.push(key);
        }
        
        return parts.sort().join('+');
    }

    isInputFocused() {
        const activeElement = document.activeElement;
        return activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.contentEditable === 'true' ||
            activeElement.classList.contains('ql-editor') // Quill editor
        );
    }

    isGlobalShortcut(e) {
        const key = this.getKeyFromEvent(e);
        const globalShortcuts = [
            'ctrl+k', 'ctrl+/', 'escape', 'ctrl+shift+t', 'f1'
        ];
        return globalShortcuts.includes(key);
    }

    // Action handlers
    handleNewRecord() {
        const currentPath = window.location.pathname;
        const newRecordUrls = {
            '/sales': '/sales/customers/add',
            '/inventory': '/inventory/products/add',
            '/hr': '/hr/employees/add',
            '/finance': '/finance/invoices/create',
            '/procurement': '/procurement/suppliers/add',
            '/projects': '/projects/create'
        };

        const baseModule = Object.keys(newRecordUrls).find(path => 
            currentPath.startsWith(path)
        );

        if (baseModule) {
            window.location.href = newRecordUrls[baseModule];
        } else {
            // Show quick add menu
            this.showQuickAddMenu();
        }
    }

    handleSave() {
        const form = document.querySelector('form:not([data-no-shortcut])');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
    }

    handleEdit() {
        const editBtn = document.querySelector('[data-action="edit"], .btn-edit');
        if (editBtn) {
            editBtn.click();
        }
    }

    handleDelete() {
        const deleteBtn = document.querySelector('[data-action="delete"], .btn-delete');
        if (deleteBtn) {
            deleteBtn.click();
        }
    }

    closeModals() {
        // Close Bootstrap modals
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });

        // Close dropdowns
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });

        // Close search results
        if (window.globalSearch) {
            window.globalSearch.hideResults();
        }
    }

    navigateToModule(module, action = null) {
        let url = `/${module}`;
        if (action) {
            url += `/${action.replace('_', '/')}`;
        }
        window.location.href = url;
    }

    showShortcutsModal() {
        if (this.modal) {
            const modal = new bootstrap.Modal(this.modal);
            modal.show();
            this.updateShortcutsModal();
        }
    }

    updateShortcutsModal() {
        const modalBody = this.modal?.querySelector('.modal-body');
        if (!modalBody) return;

        const categories = this.groupShortcutsByCategory();
        
        modalBody.innerHTML = Object.keys(categories).map(category => `
            <div class="shortcut-category mb-4">
                <h6 class="text-primary mb-3">${category}</h6>
                <div class="row">
                    ${categories[category].map(shortcut => `
                        <div class="col-md-6 mb-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="shortcut-description">${shortcut.description}</span>
                                <kbd class="shortcut-keys">${this.formatShortcut(shortcut.combination)}</kbd>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
    }

    groupShortcutsByCategory() {
        const categories = {};
        
        this.shortcuts.forEach(shortcut => {
            const category = shortcut.category;
            if (!categories[category]) {
                categories[category] = [];
            }
            categories[category].push(shortcut);
        });

        return categories;
    }

    formatShortcut(combination) {
        return combination
            .split('+')
            .map(key => {
                const keyMap = {
                    'ctrl': 'Ctrl',
                    'alt': 'Alt',
                    'shift': 'Shift',
                    'meta': 'Cmd',
                    'escape': 'Esc',
                    'arrowup': '↑',
                    'arrowdown': '↓',
                    'arrowleft': '←',
                    'arrowright': '→'
                };
                return keyMap[key.toLowerCase()] || key.toUpperCase();
            })
            .join(' + ');
    }

    showQuickAddMenu() {
        // Create and show a quick add menu
        const menu = document.createElement('div');
        menu.className = 'quick-add-menu';
        menu.innerHTML = `
            <div class="quick-add-content">
                <h6>Quick Add</h6>
                <div class="quick-add-options">
                    <a href="/sales/customers/add" class="quick-add-option">
                        <i class="fas fa-user-plus"></i> Customer
                    </a>
                    <a href="/sales/orders/add" class="quick-add-option">
                        <i class="fas fa-shopping-cart"></i> Order
                    </a>
                    <a href="/inventory/products/add" class="quick-add-option">
                        <i class="fas fa-box"></i> Product
                    </a>
                    <a href="/hr/employees/add" class="quick-add-option">
                        <i class="fas fa-user-tie"></i> Employee
                    </a>
                    <a href="/finance/invoices/create" class="quick-add-option">
                        <i class="fas fa-file-invoice"></i> Invoice
                    </a>
                </div>
            </div>
        `;

        document.body.appendChild(menu);

        // Position menu at center
        menu.style.position = 'fixed';
        menu.style.top = '50%';
        menu.style.left = '50%';
        menu.style.transform = 'translate(-50%, -50%)';
        menu.style.zIndex = '9999';

        // Close on click outside
        const closeMenu = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        };

        setTimeout(() => {
            document.addEventListener('click', closeMenu);
        }, 100);

        // Close on escape
        const closeOnEscape = (e) => {
            if (e.key === 'Escape') {
                menu.remove();
                document.removeEventListener('keydown', closeOnEscape);
            }
        };
        document.addEventListener('keydown', closeOnEscape);
    }

    showHelp() {
        // Navigate to help page or show help modal
        const helpUrl = '/help';
        window.open(helpUrl, '_blank');
    }

    // User customization
    loadUserShortcuts() {
        const userShortcuts = localStorage.getItem('userShortcuts');
        if (userShortcuts) {
            try {
                const shortcuts = JSON.parse(userShortcuts);
                Object.keys(shortcuts).forEach(key => {
                    const shortcut = shortcuts[key];
                    if (shortcut.enabled !== false) {
                        this.register(key, shortcut.callback, shortcut.description, shortcut.category);
                    }
                });
            } catch (error) {
                console.error('Failed to load user shortcuts:', error);
            }
        }
    }

    saveUserShortcuts() {
        const userShortcuts = {};
        this.shortcuts.forEach((shortcut, key) => {
            if (shortcut.userDefined) {
                userShortcuts[key] = {
                    callback: shortcut.callback.toString(),
                    description: shortcut.description,
                    category: shortcut.category,
                    enabled: true
                };
            }
        });
        localStorage.setItem('userShortcuts', JSON.stringify(userShortcuts));
    }

    // Enable/disable shortcuts
    enable() {
        this.isEnabled = true;
    }

    disable() {
        this.isEnabled = false;
    }

    toggle() {
        this.isEnabled = !this.isEnabled;
    }

    // Usage analytics
    logShortcutUsage(key) {
        const usage = JSON.parse(localStorage.getItem('shortcutUsage') || '{}');
        usage[key] = (usage[key] || 0) + 1;
        localStorage.setItem('shortcutUsage', JSON.stringify(usage));
    }

    getUsageStats() {
        return JSON.parse(localStorage.getItem('shortcutUsage') || '{}');
    }

    getMostUsedShortcuts(limit = 10) {
        const usage = this.getUsageStats();
        return Object.entries(usage)
            .sort(([,a], [,b]) => b - a)
            .slice(0, limit)
            .map(([key, count]) => ({
                key,
                count,
                shortcut: this.shortcuts.get(key)
            }));
    }
}

// Context-specific shortcuts
class ContextualShortcuts {
    constructor() {
        this.contexts = new Map();
        this.currentContext = null;
        this.init();
    }

    init() {
        this.registerContexts();
        this.bindEvents();
    }

    registerContexts() {
        // Table context
        this.registerContext('table', {
            'j': () => this.navigateTable('down'),
            'k': () => this.navigateTable('up'),
            'enter': () => this.selectTableRow(),
            'space': () => this.toggleTableRow()
        }, 'Table Navigation');

        // Form context
        this.registerContext('form', {
            'ctrl+enter': (e) => {
                e.preventDefault();
                this.submitForm();
            },
            'tab': (e) => this.handleFormTab(e),
            'shift+tab': (e) => this.handleFormShiftTab(e)
        }, 'Form Navigation');

        // Modal context
        this.registerContext('modal', {
            'escape': () => this.closeCurrentModal(),
            'enter': () => this.confirmModal(),
            'tab': (e) => this.trapFocusInModal(e)
        }, 'Modal Navigation');
    }

    registerContext(name, shortcuts, description) {
        this.contexts.set(name, {
            shortcuts: new Map(Object.entries(shortcuts)),
            description
        });
    }

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (this.currentContext) {
                const context = this.contexts.get(this.currentContext);
                if (context) {
                    const key = this.getKeyFromEvent(e);
                    const shortcut = context.shortcuts.get(key);
                    if (shortcut) {
                        shortcut(e);
                    }
                }
            }
        });

        // Auto-detect context changes
        document.addEventListener('focusin', (e) => {
            this.detectContext(e.target);
        });

        document.addEventListener('click', (e) => {
            this.detectContext(e.target);
        });
    }

    detectContext(element) {
        if (element.closest('.modal')) {
            this.setContext('modal');
        } else if (element.closest('form')) {
            this.setContext('form');
        } else if (element.closest('table, .data-table')) {
            this.setContext('table');
        } else {
            this.setContext(null);
        }
    }

    setContext(context) {
        this.currentContext = context;
        
        // Dispatch context change event
        const event = new CustomEvent('shortcutContextChanged', {
            detail: { context }
        });
        document.dispatchEvent(event);
    }

    getKeyFromEvent(e) {
        const parts = [];
        
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        if (e.metaKey) parts.push('meta');
        
        const key = e.key.toLowerCase();
        if (key !== 'control' && key !== 'alt' && key !== 'shift' && key !== 'meta') {
            parts.push(key);
        }
        
        return parts.join('+');
    }

    // Context-specific actions
    navigateTable(direction) {
        const table = document.querySelector('table:focus-within, .data-table:focus-within');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        const currentRow = table.querySelector('tbody tr.selected, tbody tr:focus-within');
        
        if (!currentRow) {
            if (rows.length > 0) {
                rows[0].focus();
            }
            return;
        }

        const currentIndex = Array.from(rows).indexOf(currentRow);
        let nextIndex;

        if (direction === 'down') {
            nextIndex = Math.min(currentIndex + 1, rows.length - 1);
        } else {
            nextIndex = Math.max(currentIndex - 1, 0);
        }

        rows[nextIndex].focus();
        rows[nextIndex].scrollIntoView({ block: 'nearest' });
    }

    selectTableRow() {
        const currentRow = document.querySelector('tbody tr:focus-within');
        if (currentRow) {
            const link = currentRow.querySelector('a');
            if (link) {
                link.click();
            }
        }
    }

    toggleTableRow() {
        const currentRow = document.querySelector('tbody tr:focus-within');
        if (currentRow) {
            const checkbox = currentRow.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
            }
        }
    }

    submitForm() {
        const form = document.querySelector('form:focus-within');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]:not(:disabled)');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }

    closeCurrentModal() {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }

    confirmModal() {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            const confirmBtn = modal.querySelector('.btn-primary, .btn-success, [data-action="confirm"]');
            if (confirmBtn && !confirmBtn.disabled) {
                confirmBtn.click();
            }
        }
    }

    trapFocusInModal(e) {
        const modal = document.querySelector('.modal.show');
        if (!modal) return;

        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
}

// Initialize shortcuts
document.addEventListener('DOMContentLoaded', () => {
    window.keyboardShortcuts = new KeyboardShortcuts();
    window.contextualShortcuts = new ContextualShortcuts();
    
    console.log('Keyboard shortcuts initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        KeyboardShortcuts,
        ContextualShortcuts
    };
}