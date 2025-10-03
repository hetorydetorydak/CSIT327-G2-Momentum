const loginBtn = document.getElementById('loginBtn');
const getStartedBtn = document.getElementById('getStartedBtn');
const loginModal = document.getElementById('loginModal');
const closeModal = document.getElementById('closeModal');
const modalBackdrop = document.querySelector('.modal-backdrop');

loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'flex';
    console.log('Login button clicked');
});

closeModal.addEventListener('click', () => {
    loginModal.style.display = 'none';
    console.log('Close button clicked');
});

modalBackdrop.addEventListener('click', () => {
    loginModal.style.display = 'none';
    console.log('Backdrop clicked');
});