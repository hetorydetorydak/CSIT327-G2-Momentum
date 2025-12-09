// User Management Functions
class UserManager {
    constructor() {
        this.currentAdminPage = 1;
        this.currentSupervisorPage = 1;
        this.currentEmployeePage = 1;
        this.adminSearchTimeout = null;
        this.supervisorSearchTimeout = null;
        this.employeeSearchTimeout = null;
        
        this.init();
    }
    
    init() {
        // Load data when sections are expanded
        this.setupToggleListeners();
        
        // Setup create buttons
        this.setupCreateButtons();
        
        // Setup search inputs
        this.setupSearchInputs();
    }
    
    setupToggleListeners() {
        const adminToggle = document.getElementById('createAdminToggle');
        const supervisorToggle = document.getElementById('createSupervisorToggle');
        const employeeToggle = document.getElementById('manageEmployeesToggle');
        
        if (adminToggle) {
            adminToggle.addEventListener('click', () => {
                setTimeout(() => {
                    if (!document.getElementById('createAdminContent').classList.contains('collapsed')) {
                        this.loadAdmins();
                    }
                }, 100);
            });
        }
        
        if (supervisorToggle) {
            supervisorToggle.addEventListener('click', () => {
                setTimeout(() => {
                    if (!document.getElementById('createSupervisorContent').classList.contains('collapsed')) {
                        this.loadSupervisors();
                    }
                }, 100);
            });
        }
        
        if (employeeToggle) {
            employeeToggle.addEventListener('click', () => {
                setTimeout(() => {
                    if (!document.getElementById('manageEmployeesContent').classList.contains('collapsed')) {
                        this.loadEmployees();
                    }
                }, 100);
            });
        }
    }
    
    setupCreateButtons() {
        const createAdminBtn = document.getElementById('createAdminBtn');
        const createSupervisorBtn = document.getElementById('createSupervisorBtn');
        
        if (createAdminBtn) {
            createAdminBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                showAdminCreateModal('admin');
            });
        }
        
        if (createSupervisorBtn) {
            createSupervisorBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                showAdminCreateModal('supervisor');
            });
        }
        
        // View all users button
        const viewAllUsersBtn = document.getElementById('viewAllUsersBtn');
        if (viewAllUsersBtn) {
            viewAllUsersBtn.addEventListener('click', () => {
                this.loadAllUsers();
            });
        }
    }
    
    setupSearchInputs() {
        const adminSearch = document.getElementById('searchAdminInput');
        const supervisorSearch = document.getElementById('searchSupervisorInput');
        const employeeSearch = document.getElementById('searchEmployeeInput');
        
        if (adminSearch) {
            adminSearch.addEventListener('input', (e) => {
                clearTimeout(this.adminSearchTimeout);
                this.adminSearchTimeout = setTimeout(() => {
                    this.searchAdmins(e.target.value);
                }, 500);
            });
        }
        
        if (supervisorSearch) {
            supervisorSearch.addEventListener('input', (e) => {
                clearTimeout(this.supervisorSearchTimeout);
                this.supervisorSearchTimeout = setTimeout(() => {
                    this.searchSupervisors(e.target.value);
                }, 500);
            });
        }
        
        if (employeeSearch) {
            employeeSearch.addEventListener('input', (e) => {
                clearTimeout(this.employeeSearchTimeout);
                this.employeeSearchTimeout = setTimeout(() => {
                    this.searchEmployees(e.target.value);
                }, 500);
            });
        }
    }
    
    async loadAdmins(page = 1, search = '') {
        try {
            this.showLoading('adminTableBody');
            
            const response = await fetch(`/core/admin/get-admins/?page=${page}&search=${encodeURIComponent(search)}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderAdmins(data.admins);
                this.currentAdminPage = page;
            } else {
                this.showError('adminTableBody', data.error || 'Failed to load admins');
            }
        } catch (error) {
            console.error('Error loading admins:', error);
            this.showError('adminTableBody', 'Network error loading admins');
        }
    }
    
    async loadSupervisors(page = 1, search = '') {
        try {
            this.showLoading('supervisorTableBody');
            
            const response = await fetch(`/core/admin/get-supervisors/?page=${page}&search=${encodeURIComponent(search)}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderSupervisors(data.supervisors);
                this.currentSupervisorPage = page;
            } else {
                this.showError('supervisorTableBody', data.error || 'Failed to load supervisors');
            }
        } catch (error) {
            console.error('Error loading supervisors:', error);
            this.showError('supervisorTableBody', 'Network error loading supervisors');
        }
    }
    
    async loadEmployees(page = 1, search = '') {
        try {
            this.showLoading('employeeTableBody');
            
            const response = await fetch(`/core/admin/get-employees/?page=${page}&search=${encodeURIComponent(search)}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderEmployees(data.employees);
                this.currentEmployeePage = page;
            } else {
                this.showError('employeeTableBody', data.error || 'Failed to load employees');
            }
        } catch (error) {
            console.error('Error loading employees:', error);
            this.showError('employeeTableBody', 'Network error loading employees');
        }
    }
    
    async loadAllUsers(role = 'all', page = 1, search = '') {
        try {
            this.showLoading('employeeTableBody');
            
            const response = await fetch(`/core/admin/get-all-users/?role=${role}&page=${page}&search=${encodeURIComponent(search)}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderAllUsers(data.users, data.pagination);
            } else {
                this.showError('employeeTableBody', data.error || 'Failed to load users');
            }
        } catch (error) {
            console.error('Error loading all users:', error);
            this.showError('employeeTableBody', 'Network error loading users');
        }
    }
    
    renderAdmins(admins) {
        const tbody = document.getElementById('adminTableBody');
        if (!tbody) return;
        
        if (admins.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #6b7280;">
                        No admin users found
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        admins.forEach((admin, index) => {
            const rowClass = index % 2 === 0 ? 'user-row' : 'user-row alt-row';
            const firstLoginText = admin.is_first_login ? 
                '<span style="color: #10b981; font-weight: bold;">Yes</span>' : 
                '<span style="color: #ef4444;">No</span>';
            
            html += `
                <tr class="${rowClass}" data-user-id="${admin.id}">
                    <td class="checkbox-col">
                        <input type="checkbox" class="user-checkbox table-checkbox admin-checkbox">
                    </td>
                    <td>${this.escapeHtml(admin.username)}</td>
                    <td>${this.escapeHtml(admin.employee_name)}</td>
                    <td>${this.escapeHtml(admin.email)}</td>
                    <td><span class="role-badge admin-badge">Admin</span></td>
                    <td>${firstLoginText}</td>
                    <td>${this.escapeHtml(admin.last_login)}</td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    }
    
    renderSupervisors(supervisors) {
        const tbody = document.getElementById('supervisorTableBody');
        if (!tbody) return;
        
        if (supervisors.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #6b7280;">
                        No supervisor users found
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        supervisors.forEach((supervisor, index) => {
            const rowClass = index % 2 === 0 ? 'user-row' : 'user-row alt-row';
            const firstLoginText = supervisor.is_first_login ? 
                '<span style="color: #10b981; font-weight: bold;">Yes</span>' : 
                '<span style="color: #ef4444;">No</span>';
            
            html += `
                <tr class="${rowClass}" data-user-id="${supervisor.id}">
                    <td class="checkbox-col">
                        <input type="checkbox" class="user-checkbox table-checkbox supervisor-checkbox">
                    </td>
                    <td>${this.escapeHtml(supervisor.username)}</td>
                    <td>${this.escapeHtml(supervisor.employee_name)}</td>
                    <td>${this.escapeHtml(supervisor.email)}</td>
                    <td><span class="role-badge supervisor-badge">Supervisor</span></td>
                    <td>${firstLoginText}</td>
                    <td>${this.escapeHtml(supervisor.last_login)}</td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    }
    
    renderEmployees(employees) {
        const tbody = document.getElementById('employeeTableBody');
        if (!tbody) return;
        
        if (employees.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #6b7280;">
                        No employee users found
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        employees.forEach((employee, index) => {
            const rowClass = index % 2 === 0 ? 'user-row' : 'user-row alt-row';
            const firstLoginText = employee.is_first_login ? 
                '<span style="color: #ef4444; font-weight: bold;">Yes</span>' : 
                '<span style="color: #10b981;">No</span>';
            
            html += `
                <tr class="${rowClass}" data-user-id="${employee.id}">
                    <td class="checkbox-col">
                        <input type="checkbox" class="user-checkbox table-checkbox employee-checkbox">
                    </td>
                    <td>${this.escapeHtml(employee.username)}</td>
                    <td>${this.escapeHtml(employee.employee_name)}</td>
                    <td>${this.escapeHtml(employee.email)}</td>
                    <td><span class="role-badge employee-badge">Employee</span></td>
                    <td>${firstLoginText}</td>
                    <td>${this.escapeHtml(employee.last_login)}</td>
                    <td class="actions-cell">
                        <button class="action-btn edit-btn" onclick="userManager.editUser(${employee.id}, 'employee')">Edit</button>
                        <button class="action-btn reset-btn" onclick="userManager.resetPassword(${employee.id}, 'employee')">Reset PW</button>
                        <button class="action-btn delete-btn" onclick="userManager.deleteUser(${employee.id}, 'employee')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    }
    
    renderAllUsers(users, pagination) {
        const tbody = document.getElementById('employeeTableBody');
        if (!tbody) return;
        
        if (users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #6b7280;">
                        No users found
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        users.forEach((user, index) => {
            const rowClass = index % 2 === 0 ? 'user-row' : 'user-row alt-row';
            const firstLoginText = user.is_first_login ? 
                '<span style="color: #ef4444; font-weight: bold;">Yes</span>' : 
                '<span style="color: #10b981;">No</span>';
            
            let roleBadge = '';
            if (user.role_id === 301) {
                roleBadge = '<span class="role-badge admin-badge">Admin</span>';
            } else if (user.role_id === 302) {
                roleBadge = '<span class="role-badge supervisor-badge">Supervisor</span>';
            } else {
                roleBadge = '<span class="role-badge employee-badge">Employee</span>';
            }
            
            html += `
                <tr class="${rowClass}" data-user-id="${user.id}">
                    <td class="checkbox-col">
                        <input type="checkbox" class="user-checkbox table-checkbox all-user-checkbox">
                    </td>
                    <td>${this.escapeHtml(user.username)}</td>
                    <td>${this.escapeHtml(user.employee_name)}</td>
                    <td>${this.escapeHtml(user.email)}</td>
                    <td>${roleBadge}</td>
                    <td>${firstLoginText}</td>
                    <td>${this.escapeHtml(user.last_login)}</td>
                    <td class="actions-cell">
                        <button class="action-btn edit-btn" onclick="userManager.editUser(${user.id}, 'all')">Edit</button>
                        <button class="action-btn reset-btn" onclick="userManager.resetPassword(${user.id}, 'all')">Reset PW</button>
                        <button class="action-btn delete-btn" onclick="userManager.deleteUser(${user.id}, 'all')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
        
        // Render pagination controls
        this.renderPagination('employeePagination', pagination, 'all');
    }
    
    renderPagination(containerId, pagination, userType) {
        const container = document.getElementById(containerId);
        if (!container || !pagination) return;
        
        const { page, total_pages, has_next, has_previous } = pagination;
        
        let html = `
            <div style="display: flex; align-items: center;">
                <button class="pagination-btn" onclick="userManager.loadPage('${userType}', ${page - 1})" ${!has_previous ? 'disabled' : ''}>
                    Previous
                </button>
                
                <div class="pagination-info">
                    Page ${page} of ${total_pages}
                </div>
                
                <button class="pagination-btn" onclick="userManager.loadPage('${userType}', ${page + 1})" ${!has_next ? 'disabled' : ''}>
                    Next
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        container.style.display = 'flex';
    }
    
    async loadPage(userType, page) {
        if (page < 1) return;
        
        switch(userType) {
            case 'admin':
                await this.loadAdmins(page, document.getElementById('searchAdminInput')?.value || '');
                break;
            case 'supervisor':
                await this.loadSupervisors(page, document.getElementById('searchSupervisorInput')?.value || '');
                break;
            case 'employee':
                await this.loadEmployees(page, document.getElementById('searchEmployeeInput')?.value || '');
                break;
            case 'all':
                await this.loadAllUsers('all', page, document.getElementById('searchEmployeeInput')?.value || '');
                break;
        }
    }
    
    searchAdmins(query) {
        this.loadAdmins(1, query);
    }
    
    searchSupervisors(query) {
        this.loadSupervisors(1, query);
    }
    
    searchEmployees(query) {
        this.loadEmployees(1, query);
    }
    
    showLoading(tableBodyId) {
        const tbody = document.getElementById(tableBodyId);
        if (!tbody) return;
        
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px;">
                    <div style="display: inline-block;">
                        <div style="margin-bottom: 10px;">Loading...</div>
                        <div style="width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                    </div>
                </td>
            </tr>
        `;
    }
    
    showError(tableBodyId, message) {
        const tbody = document.getElementById(tableBodyId);
        if (!tbody) return;
        
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: #ef4444;">
                    ${this.escapeHtml(message)}
                </td>
            </tr>
        `;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Action methods
    async editUser(userId, userType) {
        alert(`Edit user ${userId} (${userType}) - To be implemented`);
        // You'll need to create an edit modal
    }
    
    async resetPassword(userId, userType) {
        if (confirm('Are you sure you want to reset this user\'s password? They will need to set a new password on next login.')) {
            try {
                const response = await fetch(`/core/admin/reset-password/${userId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Password reset successfully!');
                    // Reload the appropriate table
                    switch(userType) {
                        case 'admin':
                            this.loadAdmins();
                            break;
                        case 'supervisor':
                            this.loadSupervisors();
                            break;
                        case 'employee':
                        case 'all':
                            this.loadEmployees();
                            break;
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error resetting password:', error);
                alert('Network error resetting password');
            }
        }
    }
    
    async deleteUser(userId, userType) {
        if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            try {
                const response = await fetch(`/core/admin/delete-user/${userId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('User deleted successfully!');
                    // Reload the appropriate table
                    switch(userType) {
                        case 'admin':
                            this.loadAdmins();
                            break;
                        case 'supervisor':
                            this.loadSupervisors();
                            break;
                        case 'employee':
                        case 'all':
                            this.loadEmployees();
                            break;
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error deleting user:', error);
                alert('Network error deleting user');
            }
        }
    }
}

// Helper function to get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Initialize UserManager when DOM is loaded
let userManager;
document.addEventListener('DOMContentLoaded', function() {
    userManager = new UserManager();
    
    // Export to global scope for onclick handlers
    window.userManager = userManager;
    window.searchAdmins = (query) => userManager.searchAdmins(query);
    window.searchSupervisors = (query) => userManager.searchSupervisors(query);
    window.searchEmployees = (query) => userManager.searchEmployees(query);
});