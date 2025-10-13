const loginBtn = document.getElementById('loginBtn');
const getStartedBtn = document.getElementById('getStartedBtn');
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

  nextBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
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

      if (!allFilled) return;

      if (currentStep === 0) {
        const email = registerForm.querySelector("input[name='email']").value.trim();

        if (!emailPattern.test(email)) {
          alert("Please enter a valid email address.");
          return;
        }
      }

      if (currentStep === 1) {
        const password = registerForm.querySelector('input[name="password"]').value;
        const confirmPassword = registerForm.querySelector('input[name="confirm_password"]').value;

        if (password !== confirmPassword) {
          alert("Passwords do not match!");
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
    showLoginModal();
    
});
getStartedBtn.addEventListener('click', () => {
    showRegisterModal();
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
