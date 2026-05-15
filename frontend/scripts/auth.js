async function handleLogin() {
    const username = document.getElementById('loginEmail').value; // Using email field as username for login as per current main.py logic
    const password = document.getElementById('loginPassword').value;

    try {
        const data = await api.login(username, password);
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);
        localStorage.setItem('username', data.username);
        
        alert('Login successful!');
        redirectBasedOnRole(data.role);
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function handleRegister() {
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const role = document.getElementById('regRole').value;

    try {
        await api.register(username, email, password, role);
        alert('Registration successful! Please log in.');
        switchToLogin();
    } catch (error) {
        alert('Registration failed: ' + error.message);
    }
}

function redirectBasedOnRole(role) {
    if (role === 'admin') {
        window.location.href = 'administration_page.html';
    } else if (role === 'jury') {
        window.location.href = 'jury_homepage.html';
    } else {
        window.location.href = 'homepage.html';
    }
}

function switchToLogin() {
    document.getElementById('registerModal').classList.remove('active');
    document.getElementById('loginModal').classList.add('active');
}

function logout() {
    localStorage.clear();
    window.location.href = 'main_page.html';
}

// Check if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    if (token && window.location.pathname.endsWith('main_page.html')) {
        // redirectBasedOnRole(role);
    }
});
