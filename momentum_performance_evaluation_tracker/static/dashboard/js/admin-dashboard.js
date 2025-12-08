document.addEventListener('DOMContentLoaded', function() {
    // ----------- TOGGLE FUNCTION -----------
    function setupToggle(buttonId, contentId) {
        const toggleBtn = document.getElementById(buttonId);
        const content = document.getElementById(contentId);
        
        console.log("Setup toggle for:", buttonId);

        if (!toggleBtn || !content) {
            console.error("Missing element!", buttonId, contentId);
            return;
        }

        // Remove any existing listeners by cloning the element
        const newToggleBtn = toggleBtn.cloneNode(true);
        toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);

        newToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log("CLICK DETECTED on", buttonId);
            const isCollapsed = content.classList.contains('collapsed');
            console.log("Is collapsed:", isCollapsed);
            
            if (isCollapsed) {
                // Expand
                content.classList.remove('collapsed');
                newToggleBtn.classList.add('active');
                newToggleBtn.setAttribute('aria-expanded', 'true');
                content.setAttribute('aria-hidden', 'false');
                console.log("Expanded!");
            } else {
                // Collapse
                content.classList.add('collapsed');
                newToggleBtn.classList.remove('active');
                newToggleBtn.setAttribute('aria-expanded', 'false');
                content.setAttribute('aria-hidden', 'true');
                console.log("Collapsed!");
            }
        });
    }

    // Setup toggles
    setupToggle('createAdminToggle', 'createAdminContent');
    setupToggle('createSupervisorToggle', 'createSupervisorContent');


    // ----------- SELECT ALL CHECKBOX FUNCTION -----------
    function setupSelectAll(masterId, rowCheckboxClass) {
        const masterCheckbox = document.getElementById(masterId);
        const rowCheckboxes = document.querySelectorAll(`.${rowCheckboxClass}`);

        if (!masterCheckbox || rowCheckboxes.length === 0) return;

        masterCheckbox.addEventListener('change', function() {
            rowCheckboxes.forEach(cb => cb.checked = this.checked);
            masterCheckbox.indeterminate = false;
        });

        rowCheckboxes.forEach(cb => {
            cb.addEventListener('change', function() {
                const allChecked = Array.from(rowCheckboxes).every(c => c.checked);
                const someChecked = Array.from(rowCheckboxes).some(c => c.checked);

                masterCheckbox.checked = allChecked;
                masterCheckbox.indeterminate = someChecked && !allChecked;
            });
        });
    }

    // Setup select all for both tables
    setupSelectAll('select-admin-all', 'admin-checkbox');
    setupSelectAll('select-supervisor-all', 'supervisor-checkbox');


    // ----------- MODAL FUNCTIONALITY -----------
    console.log("Setting up modals...");
    
    // Check if modals exist
    const adminModal = document.getElementById('createAdminModal');
    const supervisorModal = document.getElementById('createSupervisorModal');
    
    console.log("Admin Modal found:", adminModal);
    console.log("Supervisor Modal found:", supervisorModal);

    // Email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Open modal function
    function openModal(modalId) {
        console.log("Opening modal:", modalId);
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            console.log("Modal opened successfully");
        } else {
            console.error("Modal not found:", modalId);
        }
    }

    // Close modal function
    function closeModal(modalId) {
        console.log("Closing modal:", modalId);
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.style.overflow = '';
            // Reset form
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                clearErrors(form);
            }
            console.log("Modal closed successfully");
        }
    }

    // Clear all error messages
    function clearErrors(form) {
        const errorMessages = form.querySelectorAll('.error-message');
        errorMessages.forEach(error => error.textContent = '');
        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => input.classList.remove('error'));
    }

    // Show error message
    function showError(inputId, message) {
        const input = document.getElementById(inputId);
        const errorSpan = document.getElementById(inputId + 'Error');
        if (input && errorSpan) {
            input.classList.add('error');
            errorSpan.textContent = message;
        }
    }

    // Validate email
    function validateEmail(email) {
        return emailRegex.test(email) && email.includes('@') && email.includes('.com');
    }

    // Form validation
    function validateForm(formId, prefix) {
        const form = document.getElementById(formId);
        clearErrors(form);
        
        let isValid = true;
        
        // Validate username
        const username = document.getElementById(prefix + 'Username').value.trim();
        if (!username) {
            showError(prefix + 'Username', 'Username is required');
            isValid = false;
        }
        
        // Validate employee name
        const employeeName = document.getElementById(prefix + 'EmployeeName').value.trim();
        if (!employeeName) {
            showError(prefix + 'EmployeeName', 'Employee name is required');
            isValid = false;
        }
        
        // Validate position
        const position = document.getElementById(prefix + 'Position').value.trim();
        if (!position) {
            showError(prefix + 'Position', 'Position is required');
            isValid = false;
        }
        
        // Validate email
        const email = document.getElementById(prefix + 'Email').value.trim();
        if (!email) {
            showError(prefix + 'Email', 'Email is required');
            isValid = false;
        } else if (!validateEmail(email)) {
            showError(prefix + 'Email', 'Please enter a valid email with @ and .com');
            isValid = false;
        }
        
        return isValid;
    }

    // Setup modal triggers on buttons
    console.log("Looking for Create buttons...");
    const allButtons = document.querySelectorAll('.btn');
    console.log("Found buttons:", allButtons.length);
    
    allButtons.forEach((btn, index) => {
        const btnText = btn.textContent.trim();
        console.log(`Button ${index}: "${btnText}"`);
        
        if (btnText === 'Create Admin') {
            console.log("Attaching click handler to Create Admin button");
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("Create Admin button clicked!");
                openModal('createAdminModal');
            });
        } else if (btnText === 'Create Supervisor') {
            console.log("Attaching click handler to Create Supervisor button");
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("Create Supervisor button clicked!");
                openModal('createSupervisorModal');
            });
        }
    });

    // Close button handlers
    document.querySelectorAll('.close-modal, .btn-cancel').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            closeModal(modalId);
        });
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });

    // Form submissions
    const adminForm = document.getElementById('createAdminForm');
    if (adminForm) {
        adminForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (validateForm('createAdminForm', 'admin')) {
                const formData = {
                    username: document.getElementById('adminUsername').value.trim(),
                    employeeName: document.getElementById('adminEmployeeName').value.trim(),
                    position: document.getElementById('adminPosition').value.trim(),
                    email: document.getElementById('adminEmail').value.trim(),
                    role: 'Admin'
                };
                
                console.log('Admin form submitted:', formData);
                // TODO: Send data to backend
                alert('Admin created successfully!');
                closeModal('createAdminModal');
            }
        });
    }

    const supervisorForm = document.getElementById('createSupervisorForm');
    if (supervisorForm) {
        supervisorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (validateForm('createSupervisorForm', 'supervisor')) {
                const formData = {
                    username: document.getElementById('supervisorUsername').value.trim(),
                    employeeName: document.getElementById('supervisorEmployeeName').value.trim(),
                    position: document.getElementById('supervisorPosition').value.trim(),
                    email: document.getElementById('supervisorEmail').value.trim(),
                    role: 'Supervisor'
                };
                
                console.log('Supervisor form submitted:', formData);
                // TODO: Send data to backend
                alert('Supervisor created successfully!');
                closeModal('createSupervisorModal');
            }
        });
    }
});