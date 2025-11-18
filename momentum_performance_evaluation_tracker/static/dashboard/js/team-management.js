class TeamManager {
    constructor() {
        this.selectedEmployees = new Set();
        this.modal = null;
        this.initialize();
    }

    initialize() {
        this.bindEvents();
        this.createModal();
    }

    bindEvents() {
        // Open modal when Add Employee button is clicked
        const openBtn = document.getElementById('openAddEmployeeModal');
        if (openBtn) {
            openBtn.addEventListener('click', () => this.openModal());
        }
    }

    createModal() {
        // Modal is already in HTML, just get reference
        this.modal = document.getElementById('addEmployeeModal');
        
        if (!this.modal) {
            console.error('Add Employee modal not found');
            return;
        }

        this.bindModalEvents();
    }

    bindModalEvents() {
        // Close modal events
        const closeBtn = this.modal.querySelector('.close-modal');
        const cancelBtn = this.modal.querySelector('.btn-cancel');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal());
        }
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeModal());
        }

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Search functionality
        const searchInput = this.modal.querySelector('#employeeSearch');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchEmployees(e.target.value);
                }, 300);
            });
        }

        // Add to team button
        const addBtn = this.modal.querySelector('.btn-add-to-team');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addEmployeesToTeam());
        }

        // Load initial employees
        this.searchEmployees('');
    }

    openModal() {
        if (this.modal) {
            this.modal.classList.remove('hidden');
            this.selectedEmployees.clear();
            this.updateSelectionInfo();
            this.updateAddButton();
        }
    }

    closeModal() {
        if (this.modal) {
            this.modal.classList.add('hidden');
            this.selectedEmployees.clear();
        }
    }

    async searchEmployees(query) {
        const employeesList = document.getElementById('employeesList');
        if (!employeesList) return;

        employeesList.innerHTML = '<div class="loading-message">Searching employees...</div>';

        try {
            const response = await fetch(`${window.teamManagementConfig.searchUrl}?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                this.displayEmployees(data.employees);
            } else {
                throw new Error(data.error || 'Failed to search employees');
            }
        } catch (error) {
            console.error('Error searching employees:', error);
            employeesList.innerHTML = '<div class="empty-message">Error loading employees. Please try again.</div>';
        }
    }

    displayEmployees(employees) {
        const employeesList = document.getElementById('employeesList');
        
        if (!employees.length) {
            employeesList.innerHTML = '<div class="empty-message">No employees found matching your search.</div>';
            return;
        }

        employeesList.innerHTML = employees.map(employee => `
            <div class="employee-card" data-employee-id="${employee.id}">
                <div class="employee-avatar-modal">
                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="Employee Avatar">
                </div>
                <div class="employee-info-modal">
                    <h4 class="employee-name-modal">${employee.full_name}</h4>
                    <div class="employee-details-modal">
                        <span><strong>Department:</strong> ${employee.department}</span>
                        <span><strong>Position:</strong> ${employee.position}</span>
                        <span><strong>Email:</strong> ${employee.email}</span>
                        ${employee.hire_date !== 'Not specified' ? `<span><strong>Hire Date:</strong> ${employee.hire_date}</span>` : ''}
                    </div>
                </div>
                <button class="add-to-team-btn" onclick="teamManager.toggleEmployeeSelection(${employee.id})">
                    Add to Team
                </button>
            </div>
        `).join('');
    }

    toggleEmployeeSelection(employeeId) {
        const employeeCard = document.querySelector(`.employee-card[data-employee-id="${employeeId}"]`);
        const addButton = employeeCard?.querySelector('.add-to-team-btn');
        
        if (!employeeCard || !addButton) return;

        if (this.selectedEmployees.has(employeeId)) {
            // Deselect
            this.selectedEmployees.delete(employeeId);
            employeeCard.classList.remove('selected');
            addButton.textContent = 'Add to Team';
            addButton.classList.remove('added');
        } else {
            // Select
            this.selectedEmployees.add(employeeId);
            employeeCard.classList.add('selected');
            addButton.textContent = 'Selected ✓';
            addButton.classList.add('added');
        }

        this.updateSelectionInfo();
        this.updateAddButton();
    }

    updateSelectionInfo() {
        const selectedCount = document.getElementById('selectedCount');
        if (selectedCount) {
            selectedCount.textContent = this.selectedEmployees.size;
        }
    }

    updateAddButton() {
        const addBtn = this.modal.querySelector('.btn-add-to-team');
        if (addBtn) {
            addBtn.disabled = this.selectedEmployees.size === 0;
        }
    }

    async addEmployeesToTeam() {
        if (this.selectedEmployees.size === 0) return;

        const addBtn = this.modal.querySelector('.btn-add-to-team');
        const originalText = addBtn.textContent;
        
        addBtn.disabled = true;
        addBtn.textContent = 'Adding...';

        try {
            const formData = new FormData();
            this.selectedEmployees.forEach(id => {
                formData.append('employee_ids[]', id);
            });

            const response = await fetch(window.teamManagementConfig.addToTeamUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showSuccessMessage(data.message);
                this.closeModal();
                setTimeout(() => location.reload(), 1500);
            } else {
                throw new Error(data.error || 'Failed to add employees to team');
            }
        } catch (error) {
            console.error('Error adding employees to team:', error);
            alert('Error adding employees to team: ' + error.message);
        } finally {
            addBtn.disabled = false;
            addBtn.textContent = originalText;
        }
    }

    showSuccessMessage(message) {
        alert(message);
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.teamManager = new TeamManager();
});