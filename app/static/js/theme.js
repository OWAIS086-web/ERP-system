// Theme Management for ERP System

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.bindEvents();
        this.updateThemeIcon();
        this.loadAllSettings();
    }

    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    applyTheme(theme) {
        if (theme === 'auto') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-bs-theme', systemTheme);
            document.documentElement.setAttribute('data-theme', systemTheme);
            this.currentTheme = 'auto';
            localStorage.setItem('theme', 'auto');
            localStorage.setItem('actualTheme', systemTheme);
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme);
            document.documentElement.setAttribute('data-theme', theme);
            this.currentTheme = theme;
            localStorage.setItem('theme', theme);
            localStorage.setItem('actualTheme', theme);
        }
        
        this.updateThemeIcon();
        this.dispatchThemeChange(theme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');
        
        if (themeIcon) {
            if (this.currentTheme === 'dark') {
                themeIcon.className = 'fas fa-moon';
            } else {
                themeIcon.className = 'fas fa-sun';
            }
        }
        
        if (themeText) {
            themeText.textContent = this.currentTheme === 'dark' ? 'Dark' : 'Light';
        }
    }

    bindEvents() {
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (this.getStoredTheme() === 'auto') {
                this.applyTheme('auto');
            }
        });

        // Keyboard shortcut for opening settings (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                // Open settings page instead of toggling theme
                window.location.href = '/settings';
            }
        });
    }

    loadAllSettings() {
        // Load and apply all appearance settings globally
        this.loadColorScheme();
        this.loadDisplayOptions();
        this.loadFontSettings();
    }

    loadColorScheme() {
        const savedScheme = localStorage.getItem('colorScheme') || 'default';
        this.applyColorScheme(savedScheme);
    }

    loadDisplayOptions() {
        // Compact mode
        const compactMode = localStorage.getItem('compactMode') === 'true';
        document.body.classList.toggle('compact-mode', compactMode);
        
        // Animations
        const animations = localStorage.getItem('animations') !== 'false';
        document.body.classList.toggle('no-animations', !animations);
        
        // High contrast
        const highContrast = localStorage.getItem('highContrast') === 'true';
        document.body.classList.toggle('high-contrast', highContrast);
        
        // Sidebar collapsed
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed && window.sidebarManager) {
            window.sidebarManager.isCollapsed = true;
            window.sidebarManager.updateSidebarState();
        }
    }

    loadFontSettings() {
        const fontSize = localStorage.getItem('fontSize') || 'medium';
        const fontFamily = localStorage.getItem('fontFamily') || 'inter';
        
        document.documentElement.setAttribute('data-font-size', fontSize);
        document.documentElement.setAttribute('data-font-family', fontFamily);
    }

    applyColorScheme(scheme) {
        // Remove existing color scheme classes
        document.documentElement.classList.remove(
            'scheme-default', 'scheme-ocean', 'scheme-forest', 
            'scheme-sunset', 'scheme-purple', 'scheme-emerald'
        );
        
        // Apply new color scheme
        document.documentElement.classList.add(`scheme-${scheme}`);
        localStorage.setItem('colorScheme', scheme);
        
        // Apply color scheme variables
        const colorSchemes = {
            default: {
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#8b5cf6'
            },
            ocean: {
                primary: '#0ea5e9',
                secondary: '#0284c7',
                accent: '#0369a1'
            },
            forest: {
                primary: '#059669',
                secondary: '#047857',
                accent: '#065f46'
            },
            sunset: {
                primary: '#f97316',
                secondary: '#ea580c',
                accent: '#dc2626'
            },
            purple: {
                primary: '#8b5cf6',
                secondary: '#7c3aed',
                accent: '#6d28d9'
            },
            emerald: {
                primary: '#10b981',
                secondary: '#059669',
                accent: '#047857'
            }
        };
        
        if (colorSchemes[scheme]) {
            const colors = colorSchemes[scheme];
            const root = document.documentElement;
            root.style.setProperty('--primary-color', colors.primary);
            root.style.setProperty('--secondary-color', colors.secondary);
            root.style.setProperty('--accent-color', colors.accent);
        }
    }

    animateThemeToggle(button) {
        button.style.transform = 'scale(0.9) rotate(180deg)';
        setTimeout(() => {
            button.style.transform = 'scale(1) rotate(0deg)';
        }, 200);
    }

    dispatchThemeChange(theme) {
        const event = new CustomEvent('themeChanged', {
            detail: { theme }
        });
        document.dispatchEvent(event);
    }

    // Public API
    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (['light', 'dark', 'auto'].includes(theme)) {
            this.applyTheme(theme);
        }
    }

    setColorScheme(scheme) {
        this.applyColorScheme(scheme);
    }

    setDisplayOption(option, value) {
        switch (option) {
            case 'compactMode':
                document.body.classList.toggle('compact-mode', value);
                localStorage.setItem('compactMode', value);
                break;
            case 'animations':
                document.body.classList.toggle('no-animations', !value);
                localStorage.setItem('animations', value);
                break;
            case 'highContrast':
                document.body.classList.toggle('high-contrast', value);
                localStorage.setItem('highContrast', value);
                break;
            case 'sidebarCollapsed':
                localStorage.setItem('sidebarCollapsed', value);
                if (window.sidebarManager) {
                    window.sidebarManager.isCollapsed = value;
                    window.sidebarManager.updateSidebarState();
                }
                break;
        }
    }

    setFontSettings(fontSize, fontFamily) {
        if (fontSize) {
            document.documentElement.setAttribute('data-font-size', fontSize);
            localStorage.setItem('fontSize', fontSize);
        }
        if (fontFamily) {
            document.documentElement.setAttribute('data-font-family', fontFamily);
            localStorage.setItem('fontFamily', fontFamily);
        }
    }
}


// Color Scheme Utilities
class ColorSchemeUtils {
    static getThemeColors(theme = null) {
        const currentTheme = theme || document.documentElement.getAttribute('data-theme') || 'light';
        
        const colors = {
            light: {
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#8b5cf6',
                success: '#10b981',
                warning: '#f59e0b',
                danger: '#ef4444',
                info: '#06b6d4',
                textPrimary: '#1f2937',
                textSecondary: '#4b5563',
                textMuted: '#9ca3af',
                glassBg: 'rgba(255, 255, 255, 0.25)',
                glassBorder: 'rgba(255, 255, 255, 0.18)'
            },
            dark: {
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#8b5cf6',
                success: '#10b981',
                warning: '#f59e0b',
                danger: '#ef4444',
                info: '#06b6d4',
                textPrimary: '#f8fafc',
                textSecondary: '#cbd5e1',
                textMuted: '#64748b',
                glassBg: 'rgba(15, 23, 42, 0.25)',
                glassBorder: 'rgba(255, 255, 255, 0.1)'
            }
        };

        return colors[currentTheme] || colors.light;
    }

    static getCSSVariable(variableName) {
        return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
    }

    static setCSSVariable(variableName, value) {
        document.documentElement.style.setProperty(variableName, value);
    }

    static generateGradient(color1, color2, direction = '135deg') {
        return `linear-gradient(${direction}, ${color1}, ${color2})`;
    }

    static hexToRgba(hex, alpha = 1) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    static adjustBrightness(color, amount) {
        const usePound = color[0] === '#';
        const col = usePound ? color.slice(1) : color;
        const num = parseInt(col, 16);
        let r = (num >> 16) + amount;
        let g = (num >> 8 & 0x00FF) + amount;
        let b = (num & 0x0000FF) + amount;
        
        r = r > 255 ? 255 : r < 0 ? 0 : r;
        g = g > 255 ? 255 : g < 0 ? 0 : g;
        b = b > 255 ? 255 : b < 0 ? 0 : b;
        
        return (usePound ? '#' : '') + (r << 16 | g << 8 | b).toString(16).padStart(6, '0');
    }
}

// Theme Presets
class ThemePresets {
    static presets = {
        default: {
            name: 'Default',
            colors: {
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#8b5cf6'
            }
        },
        ocean: {
            name: 'Ocean',
            colors: {
                primary: '#0ea5e9',
                secondary: '#0284c7',
                accent: '#0369a1'
            }
        },
        forest: {
            name: 'Forest',
            colors: {
                primary: '#059669',
                secondary: '#047857',
                accent: '#065f46'
            }
        },
        sunset: {
            name: 'Sunset',
            colors: {
                primary: '#f97316',
                secondary: '#ea580c',
                accent: '#dc2626'
            }
        },
        purple: {
            name: 'Purple',
            colors: {
                primary: '#8b5cf6',
                secondary: '#7c3aed',
                accent: '#6d28d9'
            }
        }
    };

    static applyPreset(presetName) {
        const preset = this.presets[presetName];
        if (!preset) return false;

        const { colors } = preset;
        ColorSchemeUtils.setCSSVariable('--primary-color', colors.primary);
        ColorSchemeUtils.setCSSVariable('--secondary-color', colors.secondary);
        ColorSchemeUtils.setCSSVariable('--accent-color', colors.accent);

        localStorage.setItem('themePreset', presetName);
        
        // Dispatch preset change event
        const event = new CustomEvent('themePresetChanged', {
            detail: { preset: presetName, colors }
        });
        document.dispatchEvent(event);

        return true;
    }

    static getCurrentPreset() {
        return localStorage.getItem('themePreset') || 'default';
    }

    static getPresetList() {
        return Object.keys(this.presets).map(key => ({
            key,
            ...this.presets[key]
        }));
    }
}

// Auto Theme Scheduler
class AutoThemeScheduler {
    constructor() {
        this.schedule = this.getStoredSchedule();
        this.isEnabled = this.getScheduleEnabled();
        this.init();
    }

    init() {
        if (this.isEnabled) {
            this.startScheduler();
        }
    }

    getStoredSchedule() {
        const stored = localStorage.getItem('themeSchedule');
        return stored ? JSON.parse(stored) : {
            lightStart: '06:00',
            darkStart: '18:00'
        };
    }

    getScheduleEnabled() {
        return localStorage.getItem('themeScheduleEnabled') === 'true';
    }

    setSchedule(lightStart, darkStart) {
        this.schedule = { lightStart, darkStart };
        localStorage.setItem('themeSchedule', JSON.stringify(this.schedule));
        
        if (this.isEnabled) {
            this.applyScheduledTheme();
        }
    }

    enableSchedule(enabled) {
        this.isEnabled = enabled;
        localStorage.setItem('themeScheduleEnabled', enabled.toString());
        
        if (enabled) {
            this.startScheduler();
        } else {
            this.stopScheduler();
        }
    }

    startScheduler() {
        this.applyScheduledTheme();
        
        // Check every minute
        this.schedulerInterval = setInterval(() => {
            this.applyScheduledTheme();
        }, 60000);
    }

    stopScheduler() {
        if (this.schedulerInterval) {
            clearInterval(this.schedulerInterval);
            this.schedulerInterval = null;
        }
    }

    applyScheduledTheme() {
        const now = new Date();
        const currentTime = now.getHours().toString().padStart(2, '0') + ':' + 
                           now.getMinutes().toString().padStart(2, '0');
        
        const lightTime = this.schedule.lightStart;
        const darkTime = this.schedule.darkStart;
        
        let shouldBeDark;
        
        if (lightTime < darkTime) {
            // Normal day (light in morning, dark in evening)
            shouldBeDark = currentTime >= darkTime || currentTime < lightTime;
        } else {
            // Inverted day (dark in morning, light in evening)
            shouldBeDark = currentTime >= darkTime && currentTime < lightTime;
        }
        
        const targetTheme = shouldBeDark ? 'dark' : 'light';
        const currentTheme = document.documentElement.getAttribute('data-theme');
        
        if (currentTheme !== targetTheme) {
            window.themeManager?.setTheme(targetTheme);
        }
    }

    getNextThemeChange() {
        const now = new Date();
        const currentTime = now.getHours().toString().padStart(2, '0') + ':' + 
                           now.getMinutes().toString().padStart(2, '0');
        
        const lightTime = this.schedule.lightStart;
        const darkTime = this.schedule.darkStart;
        
        let nextChange, nextTheme;
        
        if (currentTime < lightTime) {
            nextChange = lightTime;
            nextTheme = 'light';
        } else if (currentTime < darkTime) {
            nextChange = darkTime;
            nextTheme = 'dark';
        } else {
            nextChange = lightTime;
            nextTheme = 'light';
        }
        
        return { time: nextChange, theme: nextTheme };
    }
}

// Initialize theme system
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme manager
    window.themeManager = new ThemeManager();
    
    // Initialize auto scheduler
    window.autoThemeScheduler = new AutoThemeScheduler();
    
    // Make utilities globally available
    window.ColorSchemeUtils = ColorSchemeUtils;
    window.ThemePresets = ThemePresets;
    
    // Theme change event listeners
    document.addEventListener('themeChanged', (e) => {
        console.log('Theme changed to:', e.detail.theme);
        
        // Update any theme-dependent components
        updateThemeDependentComponents(e.detail.theme);
    });
    
    document.addEventListener('themePresetChanged', (e) => {
        console.log('Theme preset changed to:', e.detail.preset);
    });
});

// Update components that depend on theme
function updateThemeDependentComponents(theme) {
    // Update charts if they exist
    if (window.chartInstances) {
        Object.values(window.chartInstances).forEach(chart => {
            updateChartTheme(chart, theme);
        });
    }
    
    // Update data tables if they exist
    if ($.fn.DataTable) {
        $('.data-table').each(function() {
            const table = $(this).DataTable();
            if (table) {
                table.draw();
            }
        });
    }
    
    // Update any custom components
    const event = new CustomEvent('themeComponentUpdate', {
        detail: { theme }
    });
    document.dispatchEvent(event);
}

// Chart theme update helper
function updateChartTheme(chart, theme) {
    const colors = ColorSchemeUtils.getThemeColors(theme);
    
    if (chart && chart.options) {
        // Update text colors
        if (chart.options.plugins && chart.options.plugins.legend) {
            chart.options.plugins.legend.labels.color = colors.textSecondary;
        }
        
        if (chart.options.scales) {
            Object.keys(chart.options.scales).forEach(scaleKey => {
                const scale = chart.options.scales[scaleKey];
                if (scale.ticks) scale.ticks.color = colors.textMuted;
                if (scale.grid) scale.grid.color = ColorSchemeUtils.hexToRgba(colors.textMuted, 0.1);
            });
        }
        
        chart.update();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ThemeManager,
        ColorSchemeUtils,
        ThemePresets,
        AutoThemeScheduler
    };
}