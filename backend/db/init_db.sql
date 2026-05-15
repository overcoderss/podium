-- 1. Користувачі
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'jury', 'student')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Сесії (кілька пристроїв)
CREATE TABLE IF NOT EXISTS User_Sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    device_info TEXT,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 3. Турніри (з налаштуваннями лімітів)
CREATE TABLE IF NOT EXISTS Tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('draft', 'registration', 'running', 'finished')) DEFAULT 'draft',
    reg_start DATETIME,
    reg_end DATETIME,
    min_team_size INTEGER DEFAULT 2,
    max_team_size INTEGER DEFAULT 5,
    is_public BOOLEAN DEFAULT 1
);

-- 4. Команди
CREATE TABLE IF NOT EXISTS Teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE,
    captain_id INTEGER NOT NULL,
    school_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (captain_id) REFERENCES Users(id),
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(id)
);

-- 5. Склад команд
CREATE TABLE IF NOT EXISTS Team_Members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- 6. Завдання (Раунди)
CREATE TABLE IF NOT EXISTS Tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline DATETIME,
    must_have_criteria TEXT,
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(id)
);

-- 7. Сабміти (Рішення)
CREATE TABLE IF NOT EXISTS Submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    github_link TEXT,
    video_link TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES Tasks(id),
    FOREIGN KEY (team_id) REFERENCES Teams(id)
);

-- 8. Оцінки журі
CREATE TABLE IF NOT EXISTS Grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    jury_id INTEGER NOT NULL,
    criterion_name TEXT NOT NULL,
    score INTEGER CHECK(score >= 0 AND score <= 100),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES Submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (jury_id) REFERENCES Users(id)
);