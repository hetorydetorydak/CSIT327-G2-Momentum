document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profile-toggle-btn');
    const dropdownMenu = document.getElementById('profile-dropdown-menu');
    const dropdownIcon = document.getElementById('dropdown-icon');
    const logoutLink = document.querySelector('.logout-link');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogout = document.getElementById('cancelLogout');
    const confirmLogout = document.getElementById('confirmLogout');

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
            window.location.href = '/logout/'; // Redirect to Django logout URL
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
});
