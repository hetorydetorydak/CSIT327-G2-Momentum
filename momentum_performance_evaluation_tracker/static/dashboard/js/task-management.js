class TaskManager {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.bindEvents();
        this.loadEmployeeTasks();
    }

    bindEvents() {
        // Bind any task-related events here
    }


    uploadTaskFile(taskId) {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt,.zip,.rar';

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;

            if (file.size > 10 * 1024 * 1024) {
                this.showNotification('File size must be under 10MB', 'error');
                return;
            }

            this.uploadFileToServer(taskId, file);
        };

        fileInput.click();
    }

    uploadFileToServer(taskId, file) {
        const formData = new FormData();
        formData.append('task_file', file);

        fetch(`/dashboard/api/tasks/${taskId}/upload-file/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('File uploaded successfully!', 'success');
                    this.updateTaskStatus(taskId, 'Completed');
                    this.loadEmployeeTasks();
                } else {
                    this.showNotification('Upload failed: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                this.showNotification('Error uploading file', 'error');
            });
    }

    viewTaskFile(taskId) {
        fetch(`/dashboard/api/tasks/${taskId}/file-info/`)
            .then(response => response.json())
            .then(data => {
                if (data.has_file && data.file_url) {
                    window.open(data.file_url, '_blank');
                } else {
                    this.showNotification('No file available', 'info');
                }
            });
    }

    removeTaskFile(taskId) {
        if (!confirm('Are you sure you want to remove this file?')) return;

        fetch(`/dashboard/api/tasks/${taskId}/upload-file/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ remove_file: true })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('File removed successfully!', 'success');
                    this.loadEmployeeTasks();
                } else {
                    this.showNotification('Failed to remove file: ' + data.error, 'error');
                }
            });
    }

    loadEmployeeTasks() {
        fetch('/dashboard/api/tasks/employee/')
            .then(response => response.json())
            .then(data => {
                const tasksList = document.getElementById('tasksList');

                if (data.error) {
                    tasksList.innerHTML = `<div class="error-message">Unable to fetch tasks. Please try again later.</div>`;
                    return;
                }

                if (!data.tasks || data.tasks.length === 0) {
                    tasksList.innerHTML = `<div class="empty-message">No tasks assigned.</div>`;
                    return;
                }

                tasksList.innerHTML = data.tasks.map(task => `
                <div class="task-item" data-task-id="${task.id}">
                    <div class="task-content">
                        <div class="task-description">${task.description}</div>
                        <div class="task-details">
                            <span class="task-due-date">Due: ${task.due_date}</span>
                            <span class="task-priority ${task.priority.toLowerCase()}">${task.priority}</span>
                            ${task.review_status === 'Accepted' ? `
                            <span class="task-status-badge accepted" style="margin-left: 8px;">
                                <i class="fas fa-check-circle"></i> Accepted
                            </span>
                            ` : ''}
                            ${task.review_status === 'Rejected' ? `
                            <span class="task-status-badge rejected" style="margin-left: 8px;">
                                <i class="fas fa-times-circle"></i> Rejected
                            </span>
                            ` : ''}
                        </div>
                        ${task.has_file ? `
                        <div class="task-file-info">
                            <small>
                                <i class="fas fa-paperclip"></i> ${task.file_name}
                                <br>
                                <small>Uploaded: ${task.uploaded_at}</small>
                            </small>
                        </div>
                        ` : ''}
                        
                        ${task.review_status === 'Rejected' && task.review_notes ? `
                        <div class="review-feedback">
                            <small>
                                <strong>Feedback from supervisor:</strong> ${task.review_notes}
                            </small>
                        </div>
                        ` : ''}
                    </div>
                    <div class="task-actions">
                        <!-- Only show status dropdown if task is not Accepted -->
                        ${task.review_status !== 'Accepted' ? `
                        <select class="status-dropdown" onchange="window.taskManager.updateTaskStatus(${task.id}, this.value)">
                            <option value="Not Started" ${task.status === 'Not Started' ? 'selected' : ''}>Not Started</option>
                            <option value="In Progress" ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                            <option value="Completed" ${task.status === 'Completed' ? 'selected' : ''}>Completed</option>
                        </select>
                        ` : `
                        <span class="status-locked">Status: Completed ✓</span>
                        `}
                        
                        <!-- Only show upload button if task is not Accepted and not Completed yet -->
                        ${task.review_status !== 'Accepted' && task.status !== 'Completed' ? `
                        <button class="btn-file-upload" onclick="window.taskManager.uploadTaskFile(${task.id})">
                            <i class="fas fa-upload"></i> Upload
                        </button>
                        ` : ''}
                        
                        ${task.has_file ? `
                        <button class="btn-file-view" onclick="window.taskManager.viewTaskFile(${task.id})">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <!-- Only show remove file button if task is not Accepted -->
                        ${task.review_status !== 'Accepted' ? `
                        <button class="btn-file-remove" onclick="window.taskManager.removeTaskFile(${task.id})">
                            <i class="fas fa-trash"></i> Remove File
                        </button>
                        ` : ''}
                        ` : ''}
                    </div>
                </div>
            `).join('');
            })
            .catch(error => {
                console.error('Error loading tasks:', error);
                document.getElementById('tasksList').innerHTML =
                    '<div class="error-message">Unable to fetch tasks. Please try again later.</div>';
            });
    }

    updateTaskStatus(taskId, newStatus) {
        const formData = new FormData();
        formData.append('status', newStatus);

        fetch(`/dashboard/api/tasks/${taskId}/update-status/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.showNotification('Task status updated successfully!', 'success');
                    this.loadEmployeeTasks();
                } else {
                    this.showNotification('Error updating task: ' + data.error, 'error');
                    this.loadEmployeeTasks();
                }
            })
            .catch(error => {
                console.error('Error updating task:', error);
                this.showNotification('Error updating task. Please try again.', 'error');
                this.loadEmployeeTasks();
            });
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 4px;
            z-index: 1000;
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
    window.taskManager = new TaskManager();
});