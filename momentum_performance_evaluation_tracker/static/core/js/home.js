const loginBtn = document.getElementById('loginBtn');
const getStartedBtn = document.getElementById('getStartedBtn');
const heroGetStarted = document.getElementById('heroGetStarted');
const heroLearnMore = document.getElementById('heroLearnMore');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const backdrops = document.querySelectorAll('.modal-backdrop');
const closeModals = document.querySelectorAll('.modal-close');
const submitBtnLogin = document.getElementById('btnSubmitLogin');
const registerForm = document.getElementById("registerForm");
const showRegisterFromLogin = document.getElementById("showRegisterFromLogin");
const showLoginFromRegister = document.getElementById("showLoginFromRegister");
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;



let currentStep = 0;
let formSteps;
let confirmBox;

function updateStep(step) {
  formSteps.forEach((fs, i) => fs.classList.toggle("active", i === step));
}

function closeAllModals() {
  loginModal.style.display = 'none';
  registerModal.style.display = 'none';
}

function showRegisterModal() {
    closeAllModals();
    registerModal.style.display = 'flex';
}
function showLoginModal() {
    closeAllModals();
    loginModal.style.display = 'flex';
}
function resetRegisterForm() {
  registerForm.reset();
  currentStep = 0;

  // reset input styles
  registerForm.querySelectorAll("input, select, textarea").forEach(input => {
    input.style.border = "1px solid #d1d5db";
    input.style.backgroundColor = "white";
  });

  updateStep(currentStep);
}
// Function to display messages in the registration form
function showRegisterMessage(msg) {
  const msgDiv = document.getElementById('register-message');
  msgDiv.innerHTML = `<p style="color: red;">${msg}</p>`;
}
// Function to clear messages in the registration form
function clearRegisterMessage() {
  const msgDiv = document.getElementById('register-message');
  msgDiv.innerHTML = '';
}

// Multi-step form logic
if (registerForm) {
  formSteps = registerForm.querySelectorAll(".form-step");
  const nextBtns = registerForm.querySelectorAll(".next-btn");
  const prevBtns = registerForm.querySelectorAll(".prev-btn");
  confirmBox = document.getElementById("confirmation-details");

  // Clear input styles as you type
  registerForm.querySelectorAll("input, select, textarea").forEach(input => {
    input.addEventListener("input", () => {
      input.style.border = "1px solid #d1d5db"; 
      input.style.backgroundColor = "white"; 
    });
  });
// Check if email exists via AJAX
  async function checkEmailExists(email) {
    const response = await fetch(`/core/check_email/?email=${encodeURIComponent(email)}`);
    const data = await response.json();
    return data.exists;
  }
// Check if username exists via AJAX
  async function checkUsernameExists(username) {
    const response = await fetch(`/core/check_username/?username=${encodeURIComponent(username)}`);
    const data = await response.json();
    return data.exists;
  }

  nextBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {

      clearRegisterMessage();

      const inputs = formSteps[currentStep].querySelectorAll("input, select, textarea");
      let allFilled = true;

      inputs.forEach(input => {
        if (input.hasAttribute("required") && !input.value.trim()) {
          if (input.type !== "checkbox") {
            input.style.border = "2px solid #e63946"; 
            input.style.backgroundColor = "#ffe5e5";  
          }
          allFilled = false;
        } 
      });

      if (!allFilled) {
        showRegisterMessage("Please fill in all required fields.");
        return;
      }

      if (currentStep === 0) {
        // Validate email format and uniqueness
        const emailInput = registerForm.querySelector("input[name='email']");
        const email = emailInput.value.trim();

        emailInput.style.border = "1px solid #d1d5db";
        emailInput.style.backgroundColor = "white";

        if (!emailPattern.test(email)) {
          showRegisterMessage("Please enter a valid email address.");
          emailInput.style.border = "2px solid #e63946";
          emailInput.style.backgroundColor = "#ffe5e5";
          return;
        }

        if (await checkEmailExists(email)) {
          showRegisterMessage("Email address already in use.");
          emailInput.style.border = "2px solid #e63946";
          emailInput.style.backgroundColor = "#ffe5e5";
          return;
        }
      }

      if (currentStep === 1) {
        const password = registerForm.querySelector('input[name="password"]').value;
        const confirmPassword = registerForm.querySelector('input[name="confirm_password"]').value;
        
        // Validate username uniqueness
        const usernameInput = registerForm.querySelector('input[name="username"]');
        const username = usernameInput.value.trim();

        usernameInput.style.border = "1px solid #d1d5db";
        usernameInput.style.backgroundColor = "white";

        if (password !== confirmPassword) {
          showRegisterMessage("Passwords do not match!");
          return;
        }

        if (await checkUsernameExists(username)) {
          showRegisterMessage("Username already exists.");
          usernameInput.style.border = "2px solid #e63946";
          usernameInput.style.backgroundColor = "#ffe5e5";
          return;
        }

      }

      if (currentStep < formSteps.length - 1) {
        currentStep++;
        if (currentStep === 2) {
          const formData = new FormData(registerForm);
          confirmBox.innerHTML = `
            <p><strong>First Name:</strong> ${formData.get("first_name")}</p>
            <p><strong>Last Name:</strong> ${formData.get("last_name")}</p>
            <p><strong>Email:</strong> ${formData.get("email")}</p>
            <p><strong>Date Hired:</strong> ${formData.get("date_hired")}</p>
            <p><strong>Position:</strong> ${formData.get("position")}</p>
            <p><strong>Department:</strong> ${formData.get("department")}</p>
            <p><strong>Username:</strong> ${formData.get("username")}</p>
          `;
        }
        updateStep(currentStep);
      }
    });
  });

  prevBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--;
        updateStep(currentStep);
      }
    });
  });

  updateStep(currentStep);

  registerForm.addEventListener("submit", (e) => {
    // e.preventDefault(); disable to allow form submission to server (django)
  console.log("SUBMIT FIRED");
  });
}

// Open modals
loginBtn.addEventListener('click', () => {
    console.log("LOGIN BUTTON CLICKED");
    showLoginModal();
});

getStartedBtn.addEventListener('click', () => {
    showRegisterModal();
});

heroGetStarted.addEventListener('click', () => {
    showRegisterModal();
});

heroLearnMore.addEventListener('click', () => {
    window.location.href = "#about-section";
});

showRegisterFromLogin.addEventListener('click', (e) => {
    e.preventDefault();
    showRegisterModal();
});

showLoginFromRegister.addEventListener('click', (e) => {
    e.preventDefault();
    showLoginModal();  
});

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

document.addEventListener('DOMContentLoaded', () => {
  if (window.showLogin) {
    showLoginModal();
  }
  if (window.showRegister) {
    showRegisterModal();
  }
});
