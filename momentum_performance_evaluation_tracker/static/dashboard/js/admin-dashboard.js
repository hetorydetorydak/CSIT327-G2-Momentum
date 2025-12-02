document.addEventListener('DOMContentLoaded', function() {
    // ----------- TOGGLE FUNCTION -----------
    function setupToggle(buttonId, contentId) {
        const toggleBtn = document.getElementById(buttonId);
        const content = document.getElementById(contentId);

        if (!toggleBtn || !content) return;

        const collapse = () => {
            content.classList.add('collapsed');
            content.style.maxHeight = '0px';
            content.style.paddingTop = '0px';
            content.style.paddingBottom = '0px';
            toggleBtn.classList.remove('active');
            toggleBtn.setAttribute('aria-expanded', 'false');
            content.setAttribute('aria-hidden', 'true');
        };

        const expand = () => {
            content.classList.remove('collapsed');
            content.style.maxHeight = content.scrollHeight + 'px';
            content.style.paddingTop = '';
            content.style.paddingBottom = '';
            toggleBtn.classList.add('active');
            toggleBtn.setAttribute('aria-expanded', 'true');
            content.setAttribute('aria-hidden', 'false');
        };

        // Initialize state
        if (content.classList.contains('collapsed')) {
            collapse();
        } else {
            expand();
        }

        toggleBtn.addEventListener('click', function() {
            if (content.classList.contains('collapsed')) {
                expand();
            } else {
                collapse();
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
});
