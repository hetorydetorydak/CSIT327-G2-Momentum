document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profile-toggle-btn');
    const dropdownMenu = document.getElementById('profile-dropdown-menu');
    const dropdownIcon = document.getElementById('dropdown-icon');
    const logoutLink = document.querySelector('.logout-link');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogout = document.getElementById('cancelLogout');
    const confirmLogout = document.getElementById('confirmLogout');
    const passwordResetModal = document.getElementById('passwordResetModal');
    const performanceModal = document.getElementById('performanceModal');
    const backdrops = document.querySelectorAll('.modal-backdrop');
    const closeModals = document.querySelectorAll('.modal-close');

    // Close modals
    closeModals.forEach(closeModal => {
    closeModal.addEventListener('click', () => {
        closeAllModals();
        resetRegisterForm();
    });
    });
    
    backdrops.forEach(backdrop => {
    backdrop.addEventListener('click', () => {
        closeAllModals();
        resetRegisterForm();
    });
    });

    // Handle Logout Confirmation
    if (logoutLink && logoutModal && cancelLogout && confirmLogout) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("Logout link clicked");
            logoutModal.classList.remove('hidden'); // Show modal
        });

        cancelLogout.addEventListener('click', () => {
            logoutModal.classList.add('hidden'); // Hide modal
        });

        // Confirm logout
        confirmLogout.addEventListener('click', () => {
            window.location.href = '{% url "core:logout" %}'; //use Django template tag to get logout URL
        });
    }

    if (profileBtn && dropdownMenu && dropdownIcon) {
        // Function to toggle the dropdown menu visibility
        const toggleDropdown = () => {
            const isVisible = dropdownMenu.classList.toggle('visible');
            dropdownIcon.classList.toggle('open', isVisible);
        };

        // Event listener to show/hide the menu when the button is clicked
        profileBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevents the document click listener from immediately closing it
            toggleDropdown();
        });

        // Event listener to close the menu when clicking outside of it
        document.addEventListener('click', (event) => {
            // Check if the click occurred outside the dropdown menu and the toggle button
            if (dropdownMenu.classList.contains('visible') && !dropdownMenu.contains(event.target) && event.target !== profileBtn) {
                dropdownMenu.classList.remove('visible');
                dropdownIcon.classList.remove('open');
            }
        });
    } else {
        console.error("Profile dropdown elements not found. Check dashboard.html IDs.");
    }

    // Auto-show password reset modal when page loads
    if (passwordResetModal) {
        passwordResetModal.style.display = 'flex';
    }

    // Initialize Performance Features
    initializePerformanceGauges();
    initializePerformanceSearch();
});

function getPerformanceClass(value, threshold, isBacklog = false) {
    if (isBacklog) {
        return value <= threshold ? 'good' : 'poor';
    }
    return value >= threshold ? 'good' : 'poor';
}

// Update closeAllModals function to properly handle performance modal
function closeAllModals() {
    const performanceModal = document.getElementById('performanceModal');
    if (performanceModal) {
        performanceModal.classList.add('hidden');
    }
    // Close other modals if they exist
    const addEmployeeModal = document.getElementById('addEmployeeModal');
    if (addEmployeeModal) {
        addEmployeeModal.classList.add('hidden');
    }
    const logoutModal = document.getElementById('logoutModal');
    if (logoutModal) {
        logoutModal.classList.add('hidden');
    }
}


// Performance Cards Functionality - MOVE THESE OUTSIDE DOMContentLoaded
function initializePerformanceGauges() {
    const gaugeFills = document.querySelectorAll('.gauge-fill');

    gaugeFills.forEach(gauge => {
        const score = parseFloat(gauge.getAttribute('data-score')) || 0;
        // Simple rotation: 0-100 to 0-180 degrees
        const rotation = score * 1.8;
        gauge.style.transform = `rotate(${rotation}deg)`;
    });
}

function initializePerformanceSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.performance-card');
            
            cards.forEach(card => {
                const employeeName = card.querySelector('.employee-name').textContent.toLowerCase();
                const employeePosition = card.querySelector('.employee-position').textContent.toLowerCase();
                
                if (employeeName.includes(searchTerm) || employeePosition.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Basic drilldown function
function viewEmployeeDetails(employeeId) {
    console.log('Opening performance details for employee:', employeeId);
    
    fetch(`/dashboard/modal/employee/${employeeId}/performance/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(htmlContent => {
            // Replace the entire performance modal with the new rendered content
            const oldModal = document.getElementById('performanceModal');
            if (oldModal) {
                oldModal.outerHTML = htmlContent;
            }
            
            // The modal is now visible with data, re-attach event listeners
            const newModal = document.getElementById('performanceModal');
            if (newModal) {
                newModal.classList.remove('hidden');
                
                // Re-attach close event listeners
                const closeBtn = document.getElementById('closePerformanceModal');
                if (closeBtn) {
                    closeBtn.addEventListener('click', closeAllModals);
                }
                
                const backdrop = newModal.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.addEventListener('click', closeAllModals);
                }
            }
        })
        .catch(error => {
            console.error('Error fetching employee performance:', error);
            // Show error in existing modal
            const modalBody = document.getElementById('performanceModalBody');
            if (modalBody) {
                modalBody.innerHTML = '<div class="error">Error loading performance data. Please try again.</div>';
            }
        });
}

function initializeTeamManagement() {
    // The TeamManager class will handle everything
    // It's loaded from team-management.js
}

document.addEventListener('DOMContentLoaded', () => {
    // Initialize team management
    initializeTeamManagement();
});

function removeFromTeam(employeeId) {
    if (!confirm('Are you sure you want to remove this employee from your team?')) {
        return;
    }
    
    // Show loading state
    const removeBtn = document.querySelector('.remove-from-team-btn');
    const originalText = removeBtn.textContent;
    removeBtn.textContent = 'Removing...';
    removeBtn.disabled = true;
    
    // Send remove request
    fetch(`/dashboard/api/team/remove-employee/${employeeId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Employee successfully removed from your team!');
            closeAllModals();
            // refresh the page to update the team list
            location.reload();
        } else {
            throw new Error(data.error || 'Failed to remove employee');
        }
    })
    .catch(error => {
        console.error('Error removing employee from team:', error);
        alert('Error removing employee from team: ' + error.message);
        removeBtn.textContent = originalText;
        removeBtn.disabled = false;
    });
}

// helper function to get CSRF token
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}