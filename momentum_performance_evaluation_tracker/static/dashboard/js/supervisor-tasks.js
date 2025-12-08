class SupervisorTasks {
    constructor() {
        this.currentEmployeeId = null;
        this.pendingReviewTaskId = null;
        this.pendingReviewAction = null;
        this.initialize();
    }

    initialize() {
        this.bindEvents();
        this.makeFunctionsGlobal();
    }

    bindEvents() {
        // Bind event listeners for task viewing
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-file-view')) {
                const button = e.target.closest('.btn-file-view');
                const taskId = this.extractTaskIdFromButton(button);
                if (taskId) {
                    e.preventDefault();
                    this.viewTaskFile(taskId);
                }
            }
        });
        
        // Review modal events
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'reviewNotesForm') {
                e.preventDefault();
                this.submitReviewNotes();
            }
        });
        
        document.addEventListener('click', (e) => {
            if (e.target.id === 'cancelReview' || 
                e.target.id === 'closeReviewModal' ||
                (e.target.closest && e.target.closest('#closeReviewModal'))) {
                e.preventDefault();
                this.hideReviewNotesModal();
            }
        });
        
        // Close modal when clicking on backdrop
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop') && 
                e.target.closest('#reviewNotesModal')) {
                this.hideReviewNotesModal();
            }
        });
        
        // Close with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('reviewNotesModal');
                if (modal && !modal.classList.contains('hidden')) {
                    this.hideReviewNotesModal();
                }
            }
        });
    }

    makeFunctionsGlobal() {
        // functions available globally for onclick attributes
        window.viewTaskFile = (taskId) => this.viewTaskFile(taskId);
        window.loadAllTasks = (employeeId) => this.loadAllTasks(employeeId);
        window.reviewTask = (taskId, action) => this.reviewTask(taskId, action);
    }

    extractTaskIdFromButton(button) {
        // get task ID from data attribute first
        if (button.dataset.taskId) {
            return parseInt(button.dataset.taskId);
        }
        
        // extract from onclick attribute
        const onclickAttr = button.getAttribute('onclick');
        if (onclickAttr && onclickAttr.includes('viewTaskFile')) {
            const match = onclickAttr.match(/viewTaskFile\((\d+)\)/);
            if (match) {
                return parseInt(match[1]);
            }
        }
        
        // get from parent task item
        const taskItem = button.closest('.task-item');
        if (taskItem && taskItem.dataset.taskId) {
            return parseInt(taskItem.dataset.taskId);
        }
        
        return null;
    }

    viewTaskFile(taskId) {
        console.log('Viewing file for task:', taskId);
        fetch(`/dashboard/api/tasks/${taskId}/file-info/`)
        .then(response => response.json())
        .then(data => {
            if (data.has_file && data.file_url) {
                window.open(data.file_url, '_blank');
            } else {
                this.showNotification('No file available for this task', 'info');
            }
        })
        .catch(error => {
            console.error('Error viewing file:', error);
            this.showNotification('Error viewing file', 'error');
        });
    }

    reviewTask(taskId, action) {
        // store task ID and action for the modal
        this.pendingReviewTaskId = taskId;
        this.pendingReviewAction = action;
        
        // show the review notes modal
        this.showReviewNotesModal(action);
    }

    showReviewNotesModal(action) {
        const modal = document.getElementById('reviewNotesModal');
        const modalTitle = document.getElementById('reviewModalTitle');
        const notesLabel = document.getElementById('reviewNotesLabel');
        const taskIdInput = document.getElementById('reviewTaskId');
        const actionInput = document.getElementById('reviewAction');
        
        if (!modal || !modalTitle || !taskIdInput || !actionInput) {
            // fallback to prompt if modal elements not found
            this.fallbackToPromptReview();
            return;
        }
        
        // set modal title and label based on action
        if (action === 'accept') {
            modalTitle.textContent = 'Accept Task';
            if (notesLabel) {
                notesLabel.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i> Accept Task - Notes (optional)';
            }
        } else {
            modalTitle.textContent = 'Reject Task';
            if (notesLabel) {
                notesLabel.innerHTML = '<i class="fas fa-times-circle" style="color: #ef4444;"></i> Reject Task - Notes (optional)';
            }
        }
        
        // set hidden inputs
        taskIdInput.value = this.pendingReviewTaskId;
        actionInput.value = this.pendingReviewAction;
        
        // clear textarea
        const textarea = document.getElementById('reviewNotesTextarea');
        if (textarea) {
            textarea.value = '';
        }
        
        // show modal
        modal.classList.remove('hidden');
        
        // focus on textarea
        setTimeout(() => {
            const textarea = document.getElementById('reviewNotesTextarea');
            if (textarea) {
                textarea.focus();
            }
        }, 100);
    }

    submitReviewNotes() {
        const taskId = document.getElementById('reviewTaskId')?.value;
        const action = document.getElementById('reviewAction')?.value;
        const reviewNotes = document.getElementById('reviewNotesTextarea')?.value.trim();
        
        if (!taskId || !action) {
            this.showNotification('Missing task information', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('action', action);
        if (reviewNotes) {
            formData.append('review_notes', reviewNotes);
        }
        
        // show loading state
        const submitBtn = document.getElementById('submitReview');
        if (submitBtn) {
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
        }
        
        fetch(`/dashboard/api/tasks/${taskId}/review/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Review';
            }
            
            if (data.success) {
                this.showNotification(data.message, 'success');
                this.hideReviewNotesModal();
                
                // Refresh the modal to show updated status
                setTimeout(() => {
                    if (this.currentEmployeeId) {
                        this.refreshModal(this.currentEmployeeId);
                    }
                }, 1000);
            } else {
                this.showNotification('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error reviewing task:', error);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Review';
            }
            this.showNotification('Error reviewing task', 'error');
        });
    }

    hideReviewNotesModal() {
        const modal = document.getElementById('reviewNotesModal');
        if (modal) {
            modal.classList.add('hidden');
        }
        // clear pending review data
        this.pendingReviewTaskId = null;
        this.pendingReviewAction = null;
    }

    fallbackToPromptReview() {
        // fallback to prompt if modal doesn't exist
        const reviewNotes = prompt(`Enter notes for ${this.pendingReviewAction === 'accept' ? 'acceptance' : 'rejection'} (optional):`);
        
        if (reviewNotes === null) return; // User cancelled
        
        const formData = new FormData();
        formData.append('action', this.pendingReviewAction);
        if (reviewNotes) {
            formData.append('review_notes', reviewNotes);
        }
        
        fetch(`/dashboard/api/tasks/${this.pendingReviewTaskId}/review/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message, 'success');
                // refresh the modal to show updated status
                setTimeout(() => {
                    if (this.currentEmployeeId) {
                        this.refreshModal(this.currentEmployeeId);
                    }
                }, 1000);
            } else {
                this.showNotification('Error: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error reviewing task:', error);
            this.showNotification('Error reviewing task', 'error');
        });
    }

    loadAllTasks(employeeId) {
        console.log('Loading all tasks for employee:', employeeId);
        this.showNotification('View all tasks functionality coming soon!', 'info');
        // implement based on your needs
    }

    showNotification(message, type) {
        // remove any existing notifications first
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: ${type === 'success' ? '#4CAF50' : 
                        type === 'error' ? '#f44336' : 
                        type === 'info' ? '#2196F3' : '#6b7280'};
            color: white;
            border-radius: 4px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }

    refreshModal(employeeId) {
        if (window.viewEmployeeDetails) {
            window.viewEmployeeDetails(employeeId);
        }
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    switchTaskTab(tabName) {
        const pendingSection = document.querySelector('.pending-tasks-section');
        const completedSection = document.querySelector('.completed-tasks-section');
        const pendingTab = document.querySelector('.task-tab[data-tab="pending"]');
        const completedTab = document.querySelector('.task-tab[data-tab="completed"]');
        
        if (tabName === 'pending') {
            if (pendingSection) pendingSection.style.display = 'block';
            if (completedSection) completedSection.style.display = 'none';
            if (pendingTab) pendingTab.classList.add('active');
            if (completedTab) completedTab.classList.remove('active');
        } else {
            if (pendingSection) pendingSection.style.display = 'none';
            if (completedSection) completedSection.style.display = 'block';
            if (pendingTab) pendingTab.classList.remove('active');
            if (completedTab) completedTab.classList.add('active');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.manager-dashboard') || 
        document.querySelector('[data-user-role="manager"]') ||
        window.location.pathname.includes('dashboard')) {
        
        if (!window.supervisorTasks) {
            window.supervisorTasks = new SupervisorTasks();
            console.log('Supervisor Tasks initialized');
        }
    }
});