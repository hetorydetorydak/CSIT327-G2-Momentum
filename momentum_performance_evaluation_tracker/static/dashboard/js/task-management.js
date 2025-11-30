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
                            </div>
                        </div>
                        <div class="task-actions">
                            <select class="status-dropdown" onchange="taskManager.updateTaskStatus(${task.id}, this.value)">
                                <option value="Not Started" ${task.status === 'Not Started' ? 'selected' : ''}>Not Started</option>
                                <option value="In Progress" ${task.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                <option value="Completed" ${task.status === 'Completed' ? 'selected' : ''}>Completed</option>
                                <option value="Cancelled" ${task.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                            </select>
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