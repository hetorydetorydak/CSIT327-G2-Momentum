document.addEventListener('DOMContentLoaded', function() {
    const toast = document.getElementById('attendanceToast');
    if (toast) {
        // Show toast with animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Hide toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            // Remove from DOM after animation completes
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
    }
});