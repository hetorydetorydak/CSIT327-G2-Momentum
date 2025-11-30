// Task Assignment JavaScript for Supervisor Dashboard
class TaskAssignment {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.bindEvents();
    }

    bindEvents() {
        // Bind task assignment form submission
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'assignTaskForm') {
                e.preventDefault();
                this.handleTaskAssignment(e);
            }
        });
    }

    handleTaskAssignment(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const employeeId = document.getElementById('assignEmployeeId').value;
        
        console.log('Assigning task to employee:', employeeId);
        console.log('Form data:', Object.fromEntries(formData));
        
        // Add employee_id to form data
        formData.append('employee_id', employeeId);
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Assigning...';
        
        fetch('/dashboard/api/tasks/assign/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Task assignment response:', data);
            if (data.success) {
                this.showNotification('Task assigned successfully!', 'success');
                form.reset();
                
                // Refresh the modal to show the new task in pending tasks
                setTimeout(() => {
                    const employeeId = document.getElementById('assignEmployeeId').value;
                    if (window.viewEmployeeDetails) {
                        console.log('Refreshing modal for employee:', employeeId);
                        window.viewEmployeeDetails(employeeId);
                    }
                }, 1500);
                
            } else {
                throw new Error(data.error || 'Failed to assign task');
            }
        })
        .catch(error => {
            console.error('Error assigning task:', error);
            this.showNotification('Error assigning task: ' + error.message, 'error');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
    }

    showNotification(message, type) {
        // Remove any existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 6px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.taskAssignment = new TaskAssignment();
    console.log('Task Assignment initialized');
});