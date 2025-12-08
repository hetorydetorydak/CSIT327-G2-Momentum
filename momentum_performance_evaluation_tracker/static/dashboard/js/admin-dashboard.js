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


      // ----------- ADMIN CREATE MODAL FUNCTIONALITY -----------
    const adminCreateModal = document.getElementById('adminCreateModal');
    const adminCreateForm = document.getElementById('adminCreateForm');
    const generatePasswordBtn = document.getElementById('generatePasswordBtn');
    const generatedPasswordInput = document.getElementById('generatedPassword');
    
    let currentAdminStep = 0;
    let adminFormSteps;
    let currentUserType = ''; // 'admin' or 'supervisor'
    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Initialize modal if it exists
    if (adminCreateModal) {
        const closeAdminModal = document.getElementById('closeAdminModal');
        
        // Close modal handlers
        closeAdminModal.addEventListener('click', () => {
            closeAdminCreateModal();
        });
        
        adminCreateModal.querySelector('.modal-backdrop').addEventListener('click', () => {
            closeAdminCreateModal();
        });
    }

    // Initialize form if it exists
    if (adminCreateForm) {
        adminFormSteps = adminCreateForm.querySelectorAll(".form-step");
        const adminNextBtns = adminCreateForm.querySelectorAll(".next-btn");
        const adminPrevBtns = adminCreateForm.querySelectorAll(".prev-btn");
        
        // Password generation
        if (generatePasswordBtn && generatedPasswordInput) {
            generatePasswordBtn.addEventListener('click', (e) => {
                e.preventDefault();
                generatePassword();
            });
            
            // Generate initial password
            generatePassword();
        }
        
        // Clear input styles as you type
        adminCreateForm.querySelectorAll("input, select").forEach(input => {
            input.addEventListener("input", () => {
                input.style.border = "1px solid #d1d5db"; 
                input.style.backgroundColor = "white"; 
                clearAdminMessage();
            });
        });
        
        // Next button handlers
        adminNextBtns.forEach((btn) => {
            btn.addEventListener("click", async () => {
                clearAdminMessage();
                
                const inputs = adminFormSteps[currentAdminStep].querySelectorAll("input, select");
                let allValid = true;
                
                // Validate required fields
                inputs.forEach(input => {
                    if (input.hasAttribute("required") && !input.value.trim()) {
                        input.style.border = "2px solid #e63946"; 
                        input.style.backgroundColor = "#ffe5e5";  
                        allValid = false;
                    }
                });
                
                if (!allValid) {
                    showAdminMessage("Please fill in all required fields (*)");
                    return;
                }
                
                // Step-specific validations
                if (currentAdminStep === 0) {
                    // Validate email
                    const emailInput = adminCreateForm.querySelector("input[name='email']");
                    const email = emailInput.value.trim();
                    
                    if (!emailPattern.test(email)) {
                        showAdminMessage("Please enter a valid email address.");
                        emailInput.style.border = "2px solid #e63946";
                        emailInput.style.backgroundColor = "#ffe5e5";
                        return;
                    }
                    
                    // Check if email exists via AJAX
                    try {
                        const response = await fetch(`/core/check_email/?email=${encodeURIComponent(email)}`);
                        const data = await response.json();
                        if (data.exists) {
                            showAdminMessage("Email address already in use.");
                            emailInput.style.border = "2px solid #e63946";
                            emailInput.style.backgroundColor = "#ffe5e5";
                            return;
                        }
                    } catch (error) {
                        console.error("Error checking email:", error);
                        showAdminMessage("Error checking email availability.");
                        return;
                    }
                }
                
                if (currentAdminStep === 1) {
                    // Validate username
                    const usernameInput = adminCreateForm.querySelector("input[name='username']");
                    const username = usernameInput.value.trim();
                    
                    if (!username) {
                        showAdminMessage("Username is required.");
                        usernameInput.style.border = "2px solid #e63946";
                        usernameInput.style.backgroundColor = "#ffe5e5";
                        return;
                    }
                    
                    // Check if username exists via AJAX
                    try {
                        const response = await fetch(`/core/check_username/?username=${encodeURIComponent(username)}`);
                        const data = await response.json();
                        if (data.exists) {
                            showAdminMessage("Username already exists.");
                            usernameInput.style.border = "2px solid #e63946";
                            usernameInput.style.backgroundColor = "#ffe5e5";
                            return;
                        }
                    } catch (error) {
                        console.error("Error checking username:", error);
                        showAdminMessage("Error checking username availability.");
                        return;
                    }
                    
                    // Validate password match
                    const password = generatedPasswordInput.value;
                    const confirmPassword = adminCreateForm.querySelector("input[name='confirm_password']").value;
                    
                    if (password !== confirmPassword) {
                        showAdminMessage("Passwords do not match.");
                        return;
                    }
                    
                    if (password.length < 8) {
                        showAdminMessage("Password must be at least 8 characters long.");
                        return;
                    }
                }
                
                // Move to next step
                if (currentAdminStep < adminFormSteps.length - 1) {
                    currentAdminStep++;
                    
                    // Update confirmation details on last step
                    if (currentAdminStep === 2) {
                        const formData = new FormData(adminCreateForm);
                        const confirmationDiv = document.getElementById('admin-confirmation-details');
                        
                        const userTypeDisplay = currentUserType === 'admin' ? 'Administrator' : 'Supervisor';
                        
                        let html = `
                            <p><strong>Account Type:</strong> ${userTypeDisplay}</p>
                            <p><strong>Name:</strong> ${formData.get("first_name")} ${formData.get("last_name")}</p>
                            <p><strong>Email:</strong> ${formData.get("email")}</p>
                            <p><strong>Position:</strong> ${formData.get("position") || 'Not specified'}</p>
                            <p><strong>Department:</strong> ${formData.get("department") || 'Not specified'}</p>
                            <p><strong>Username:</strong> ${formData.get("username")}</p>
                            <p><strong>Password:</strong> <span style="font-family: monospace;">${formData.get("password")}</span></p>
                            <p><strong>Require password change:</strong> ${formData.get("require_password_change") ? 'Yes' : 'No'}</p>
                        `;
                        
                        confirmationDiv.innerHTML = html;
                    }
                    
                    updateAdminStep(currentAdminStep);
                }
            });
        });
        
        // Previous button handlers
        adminPrevBtns.forEach((btn) => {
            btn.addEventListener("click", () => {
                if (currentAdminStep > 0) {
                    currentAdminStep--;
                    updateAdminStep(currentAdminStep);
                }
            });
        });
        
        // Form submission
        adminCreateForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            clearAdminMessage();
            
            // Disable submit button to prevent double submission
            const submitBtn = document.getElementById('adminCreateSubmitBtn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating...';
            submitBtn.disabled = true;
            
            try {
                const formData = new FormData(adminCreateForm);
                
                // Determine the correct endpoint based on user type
                const endpoint = currentUserType === 'admin' 
                    ? '/core/admin/create-admin/' 
                    : '/core/admin/create-supervisor/';
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAdminMessage(result.message, false);
                    
                    // Reset form and close modal after success
                    setTimeout(() => {
                        closeAdminCreateModal();
                        
                        // Refresh the page to show new user
                        location.reload();
                    }, 2000);
                } 
                // else {
                //     showAdminMessage(result.message || 'Error creating user');
                    
                //     // Highlight error fields
                //     if (result.errors) {
                //         Object.keys(result.errors).forEach(fieldName => {
                //             const input = adminCreateForm.querySelector(`[name="${fieldName}"]`);
                //             if (input) {
                //                 input.style.border = "2px solid #e63946";
                //                 input.style.backgroundColor = "#ffe5e5";
                //             }
                //         });
                //     }
                // }
            } catch (error) {
                showAdminMessage( 'Error creating user');
                console.error('Submission error:', error);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
        
        updateAdminStep(currentAdminStep);
    }

    // ----------- HELPER FUNCTIONS -----------
    function generatePassword() {
        const length = 12;
        const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*";
        let password = "";
        for (let i = 0; i < length; i++) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        generatedPasswordInput.value = password;
        
        // Also set the confirm password field
        const confirmPasswordInput = adminCreateForm.querySelector("input[name='confirm_password']");
        if (confirmPasswordInput) {
            confirmPasswordInput.value = password;
        }
    }

    function updateAdminStep(step) {
        adminFormSteps.forEach((fs, i) => fs.classList.toggle("active", i === step));
    }

    function showAdminCreateModal(userType) {
        currentUserType = userType;
        
        // Set modal title and subtitle
        const title = userType === 'admin' ? 'Create Admin Account' : 'Create Supervisor Account';
        const subtitle = userType === 'admin' 
            ? 'Admin: Create a new administrator account' 
            : 'Admin: Create a new supervisor/manager account';
        
        document.getElementById('adminModalTitle').textContent = title;
        document.getElementById('adminModalSubtitle').textContent = subtitle;
        
        // Set form action
        adminCreateForm.action = userType === 'admin' 
            ? "{% url 'core:admin_create_admin' %}" 
            : "{% url 'core:admin_create_supervisor' %}";
        
        // Reset form and show modal
        resetAdminCreateForm();
        adminCreateModal.style.display = 'flex';
    }

    function closeAdminCreateModal() {
        adminCreateModal.style.display = 'none';
        resetAdminCreateForm();
    }

    function resetAdminCreateForm() {
        if (adminCreateForm) {
            adminCreateForm.reset();
            currentAdminStep = 0;
            
            // Generate new password
            generatePassword();
            
            // Reset styles
            adminCreateForm.querySelectorAll("input, select").forEach(input => {
                input.style.border = "1px solid #d1d5db";
                input.style.backgroundColor = "white";
            });
            
            // Check the password change checkbox by default
            const passwordChangeCheckbox = document.getElementById('requirePasswordChange');
            if (passwordChangeCheckbox) {
                passwordChangeCheckbox.checked = true;
            }
            
            if (adminFormSteps) {
                updateAdminStep(currentAdminStep);
            }
        }
    }

    function showAdminMessage(msg, isError = true) {
        const msgDiv = document.getElementById('admin-create-message');
        const color = isError ? 'red' : 'green';
        const bgColor = isError ? '#ffe5e5' : '#e5ffe5';
        msgDiv.innerHTML = `<p style="color: ${color}; padding: 10px; background: ${bgColor}; border-radius: 4px; margin: 10px 0;">${msg}</p>`;
    }

    function clearAdminMessage() {
        const msgDiv = document.getElementById('admin-create-message');
        msgDiv.innerHTML = '';
    }

    // ----------- MODAL TRIGGERS -----------
    console.log("Setting up create buttons...");
    
    // Find all buttons and attach handlers
    document.querySelectorAll('.btn').forEach((btn, index) => {
        const btnText = btn.textContent.trim();
        
        if (btnText === 'Create Admin') {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("Create Admin button clicked!");
                showAdminCreateModal('admin');
            });
        } else if (btnText === 'Create Supervisor') {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log("Create Supervisor button clicked!");
                showAdminCreateModal('supervisor');
            });
        }
    });

    // Remove old modal-related code since we're using the new modal
    // Remove the old createAdminModal and createSupervisorModal modals from the DOM
    const oldAdminModal = document.getElementById('createAdminModal');
    const oldSupervisorModal = document.getElementById('createSupervisorModal');
    if (oldAdminModal) oldAdminModal.remove();
    if (oldSupervisorModal) oldSupervisorModal.remove();
});