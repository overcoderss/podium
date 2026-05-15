const API_URL = 'http://127.0.0.1:5500/';

async function apiCall(endpoint, method = 'GET', body = null, token = null) {
    const headers = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers,
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
    }

    return data;
}

const api = {
    login: (username, password) => apiCall('/login', 'POST', { username, email: '', role: '', password }),
    register: (username, email, password, role = 'team') => apiCall('/register', 'POST', { username, email, password, role }),
    getMe: (token) => apiCall('/me', 'GET', null, token),
    getTournaments: () => apiCall('/tournaments'),
    createTournament: (data, token) => apiCall('/tournaments', 'POST', data, token),
    registerTeam: (tournamentId, data, token) => apiCall(`/tournaments/${tournamentId}/register-team`, 'POST', data, token),
    getLeaderboard: (tournamentId) => apiCall(`/tournaments/${tournamentId}/leaderboard`),
    createTask: (tournamentId, data, token) => apiCall(`/tournaments/${tournamentId}/tasks`, 'POST', data, token),
    submitTask: (taskId, data, token) => apiCall(`/tasks/${taskId}/submit`, 'POST', data, token),
    assignJury: (taskId, k, token) => apiCall(`/tasks/${taskId}/assign-jury?k=${k}`, 'POST', null, token),
    getJuryAssignments: (token) => apiCall('/jury/assignments', 'GET', null, token),
    gradeSubmission: (submissionId, data, token) => apiCall(`/submissions/${submissionId}/grade`, 'POST', data, token),
};
