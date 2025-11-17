document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profile-toggle-btn');
    const dropdownMenu = document.getElementById('profile-dropdown-menu');
    const dropdownIcon = document.getElementById('dropdown-icon');
    const logoutLink = document.querySelector('.logout-link');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogout = document.getElementById('cancelLogout');
    const confirmLogout = document.getElementById('confirmLogout');
    const passwordResetModal = document.getElementById('passwordResetModal');

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
    alert(`Viewing details for employee ID: ${employeeId}`);
    // You can implement modal or redirect here
}