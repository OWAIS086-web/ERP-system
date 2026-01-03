// Main JavaScript for ERP System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Sidebar toggle functionality
    $('#sidebarToggle').click(function() {
        $('.sidebar').toggleClass('show');
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Form validation
    $('form').on('submit', function(e) {
        var form = this;
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(form).addClass('was-validated');
    });

    // AJAX setup for CSRF token
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('meta[name=csrf-token]').attr('content'));
            }
        }
    });

    // Search functionality
    $('.search-box input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();
        if (searchTerm.length > 2) {
            // Implement search logic here
            console.log('Searching for:', searchTerm);
        }
    });

    // Data table initialization
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rtip',
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }

    // Number formatting
    $('.currency').each(function() {
        var value = parseFloat($(this).text());
        if (!isNaN(value)) {
            $(this).text('$' + value.toLocaleString('en-US', {minimumFractionDigits: 2}));
        }
    });

    // Date formatting
    $('.date').each(function() {
        var date = new Date($(this).text());
        if (!isNaN(date.getTime())) {
            $(this).text(date.toLocaleDateString());
        }
    });

    // Confirmation dialogs
    $('.confirm-delete').click(function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        var message = $(this).data('message') || 'Are you sure you want to delete this item?';
        
        if (confirm(message)) {
            window.location.href = url;
        }
    });

    // Loading states
    $('.btn-loading').click(function() {
        var btn = $(this);
        var originalText = btn.text();
        btn.prop('disabled', true);
        btn.html('<span class="loading-spinner"></span> Loading...');
        
        setTimeout(function() {
            btn.prop('disabled', false);
            btn.text(originalText);
        }, 3000);
    });

    // Auto-save functionality for forms
    $('.auto-save').on('input change', function() {
        var form = $(this).closest('form');
        clearTimeout(form.data('timeout'));
        form.data('timeout', setTimeout(function() {
            saveFormData(form);
        }, 2000));
    });

    function saveFormData(form) {
        var formData = form.serialize();
        var url = form.data('auto-save-url');
        
        if (url) {
            $.ajax({
                url: url,
                method: 'POST',
                data: formData,
                success: function(response) {
                    showNotification('Data saved automatically', 'success');
                },
                error: function() {
                    showNotification('Failed to save data', 'error');
                }
            });
        }
    }

    // Notification system
    function showNotification(message, type) {
        var alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        var icon = type === 'error' ? 'fa-exclamation-triangle' : 'fa-check-circle';
        
        var notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show glass-card notification" role="alert">
                <i class="fas ${icon}"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('.flash-messages').append(notification);
        
        setTimeout(function() {
            notification.fadeOut('slow', function() {
                $(this).remove();
            });
        }, 5000);
    }

    // Chart initialization (if Chart.js is loaded)
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }

    function initializeCharts() {
        // Sales chart
        var salesCtx = document.getElementById('salesChart');
        if (salesCtx) {
            new Chart(salesCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Sales',
                        data: [12000, 19000, 15000, 25000, 22000, 30000],
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: 'rgba(255, 255, 255, 0.8)'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.6)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        y: {
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.6)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        }
    }

    // Dynamic form fields
    $('.add-field').click(function() {
        var template = $(this).data('template');
        var container = $(this).data('container');
        var newField = $(template).clone();
        $(container).append(newField);
    });

    $(document).on('click', '.remove-field', function() {
        $(this).closest('.field-group').remove();
    });

    // File upload handling
    $('.file-upload').on('change', function() {
        var input = this;
        var files = input.files;
        var preview = $(input).siblings('.file-preview');
        
        preview.empty();
        
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var fileItem = $(`
                <div class="file-item">
                    <i class="fas fa-file"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${formatFileSize(file.size)})</span>
                </div>
            `);
            preview.append(fileItem);
        }
    });

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Keyboard shortcuts
    $(document).keydown(function(e) {
        // Ctrl+S to save
        if (e.ctrlKey && e.which === 83) {
            e.preventDefault();
            var form = $('form:visible').first();
            if (form.length) {
                form.submit();
            }
        }
        
        // Escape to close modals
        if (e.which === 27) {
            $('.modal.show').modal('hide');
        }
    });

    // Initialize page-specific functionality
    var page = $('body').data('page');
    if (page && window[page + 'Init']) {
        window[page + 'Init']();
    }
});

// Global utility functions
window.ERP = {
    formatCurrency: function(amount) {
        return '$' + parseFloat(amount).toLocaleString('en-US', {minimumFractionDigits: 2});
    },
    
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    },
    
    showLoading: function(element) {
        $(element).prop('disabled', true).html('<span class="loading-spinner"></span> Loading...');
    },
    
    hideLoading: function(element, originalText) {
        $(element).prop('disabled', false).text(originalText);
    },
    
    confirmAction: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },

    getPriorityClass: function(priority) {
        const classes = {
            'critical': 'priority-critical',
            'high': 'priority-high',
            'medium': 'priority-medium',
            'low': 'priority-low'
        };
        return classes[priority] || 'priority-low';
    },

    getStatusClass: function(status) {
        const classes = {
            'critical': 'status-critical',
            'urgent': 'status-urgent',
            'high': 'status-high',
            'normal': 'status-normal',
            'low': 'status-low'
        };
        return classes[status] || 'status-normal';
    },

    formatImportantText: function(text, importance) {
        const classes = {
            'critical': 'text-critical',
            'important': 'text-important',
            'warning': 'text-warning-important',
            'success': 'text-success-important'
        };
        const className = classes[importance] || '';
        return `<span class="${className}">${text}</span>`;
    }
};

// Theme Toggle Functionality (Legacy support)
$(document).ready(function() {
    // Initialize theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Theme toggle button click (if exists)
    $('#themeToggle').click(function() {
        if (window.themeManager) {
            window.themeManager.toggleTheme();
        } else {
            // Fallback
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }
    });
});

// Initialize app function
window.initializeApp = function() {
    console.log('ERP System initialized successfully');
    
    // Initialize any additional components here
    if (window.sidebarManager) {
        console.log('Sidebar manager initialized');
    }
    
    if (window.globalSearch) {
        console.log('Global search initialized');
    }
    
    if (window.notificationManager) {
        console.log('Notification manager initialized');
    }
    
    if (window.themeManager) {
        console.log('Theme manager initialized');
    }
    
    if (window.keyboardShortcuts) {
        console.log('Keyboard shortcuts initialized');
    }
};