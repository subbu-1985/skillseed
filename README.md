 SkillSeed — Soft Skills Learning Platform

**Backend API** built with FastAPI + SQLite · For Students (Grades 6–12)

---
![WhatsApp Image 2026-03-25 at 8 27 16 PM](https://github.com/user-attachments/assets/c4dbafad-892e-48f3-b335-32465f633653)
![WhatsApp Image 2026-03-25 at 8 27 16 PM (1)](https://github.com/user-attachments/assets/4a84ac6d-c7df-44ae-b76f-043d89914936)

## ⚡ Quick Start

```bash
# 1. Clone / extract this project
cd skillseed

# 2. Run the setup + start script
chmod +x start.sh
./start.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Server:** http://localhost:8000  
**API Docs (Swagger):** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

---

## 🔐 Default Admin Account

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@skillseed.com    |
| Password | admin123               |
| Role     | admin                  |

> Created automatically on first startup via SQLite seed.

---

## 🗄️ Database

- **Engine:** SQLite (file: `skillseed.db` — created on first run)
- **ORM:** SQLAlchemy 2.0 (async)
- **No setup required** — tables are auto-created on startup

### Database Location
```
skillseed/
└── skillseed.db    ← auto-created SQLite database file
```

---

## 📁 File Storage

All uploaded files are stored **locally on disk**:

```
skillseed/
└── uploads/
    ├── videos/     ← Course videos uploaded by mentors/admins
    ├── resumes/    ← Mentor application resumes (PDF/Word)
    └── avatars/    ← User profile pictures
```

Files are served at: `http://localhost:8000/static/<type>/<filename>`

### Supported formats:
| Type    | Formats                    | Max Size  |
|---------|----------------------------|-----------|
| Videos  | .mp4, .webm, .mkv, .mov, .avi | 500MB  |
| Resumes | .pdf, .doc, .docx          | 10MB      |
| Avatars | .jpg, .jpeg, .png, .webp   | 10MB      |

---

## 🏗️ Project Structure

```
skillseed/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLite DB setup + seeder
│   ├── core/
│   │   ├── config.py           # Settings (.env)
│   │   └── security.py         # JWT auth + password hashing
│   ├── models/
│   │   ├── user.py             # User, Student, Mentor, Applications
│   │   ├── skill.py            # Skills, Modules, Levels
│   │   ├── content.py          # Videos, Activities, Progress
│   │   ├── quiz.py             # Quizzes, Questions, Attempts
│   │   ├── session.py          # Live Sessions, Attendance
│   │   ├── notification.py     # Notifications, Subscriptions,
│   │   │                       #   Badges, Messages, Languages
│   │   └── gamification.py     # Re-exports gamification models
│   └── routers/
│       ├── auth.py             # /auth/register, /auth/login
│       ├── users.py            # /users/me, avatar upload
│       ├── skills.py           # /skills, /skills/{id}/modules
│       ├── content.py          # /modules/{id}/videos (upload),
│       │                       #   /modules/{id}/activities
│       ├── quiz.py             # /quiz, /quiz/{id}/submit
│       ├── mentor.py           # /mentor/apply, /mentor/students
│       └── misc.py             # sessions, notifications, progress,
│                               #   subscriptions, admin, messaging
├── uploads/                    # File storage (auto-created)
├── skillseed.db                # SQLite DB (auto-created)
├── requirements.txt
├── start.sh
└── .env
```

---

## 🌐 API Reference

### Authentication
| Method | Endpoint         | Description         | Auth? |
|--------|-----------------|---------------------|-------|
| POST   | /auth/register  | Register new user   | ❌    |
| POST   | /auth/login     | Login, get JWT      | ❌    |

### Users
| Method | Endpoint         | Description         | Auth? |
|--------|-----------------|---------------------|-------|
| GET    | /users/me       | Get my profile      | ✅    |
| PUT    | /users/me       | Update profile      | ✅    |
| POST   | /users/me/avatar| Upload avatar image | ✅    |

### Skills
| Method | Endpoint                    | Auth?   |
|--------|----------------------------|---------|
| GET    | /skills                    | ✅ Any  |
| GET    | /skills/{id}               | ✅ Any  |
| POST   | /skills                    | 🔒 Admin|
| PUT    | /skills/{id}               | 🔒 Admin|
| DELETE | /skills/{id}               | 🔒 Admin|
| GET    | /skills/{id}/modules       | ✅ Any  |
| POST   | /skills/modules            | 🔒 Admin|

### Content (Videos & Activities)
| Method | Endpoint                              | Auth?         |
|--------|--------------------------------------|---------------|
| GET    | /modules/{id}/videos                 | ✅ Any        |
| POST   | /modules/{id}/videos                 | 🔒 Mentor+    |
| DELETE | /videos/{id}                         | 🔒 Mentor+    |
| POST   | /videos/{id}/progress                | ✅ Student    |
| GET    | /modules/{id}/activities             | ✅ Any        |
| POST   | /activities                          | 🔒 Mentor+    |
| POST   | /activities/{id}/complete            | ✅ Student    |

### Quizzes
| Method | Endpoint              | Auth?       |
|--------|-----------------------|-------------|
| GET    | /quiz/module/{id}     | ✅ Any      |
| GET    | /quiz/{id}            | ✅ Any      |
| POST   | /quiz                 | 🔒 Mentor+  |
| POST   | /quiz/{id}/submit     | ✅ Student  |

### Mentor
| Method | Endpoint                          | Auth?       |
|--------|----------------------------------|-------------|
| POST   | /mentor/apply                    | ✅ Any      |
| GET    | /mentor/applications             | 🔒 Admin    |
| POST   | /mentor/applications/{id}/review | 🔒 Admin    |
| GET    | /mentor/students                 | 🔒 Mentor+  |

### Live Sessions
| Method | Endpoint              | Auth?       |
|--------|-----------------------|-------------|
| GET    | /sessions             | ✅ Any      |
| POST   | /sessions             | 🔒 Mentor+  |
| POST   | /sessions/{id}/join   | ✅ Any      |
| DELETE | /sessions/{id}        | 🔒 Mentor+  |

### Notifications
| Method | Endpoint                    | Auth?       |
|--------|-----------------------------|-------------|
| GET    | /notifications              | ✅ Any      |
| POST   | /notifications/{id}/read    | ✅ Any      |
| POST   | /notifications/broadcast    | 🔒 Admin    |

### Progress
| Method | Endpoint        | Auth?       |
|--------|----------------|-------------|
| GET    | /progress/me   | ✅ Any      |

### Subscriptions
| Method | Endpoint               | Auth?       |
|--------|------------------------|-------------|
| GET    | /subscriptions/plans   | ❌ Public   |
| POST   | /subscriptions/plans   | 🔒 Admin    |
| POST   | /subscriptions/subscribe | ✅ Student |

### Admin
| Method | Endpoint                        | Auth?       |
|--------|---------------------------------|-------------|
| GET    | /admin/stats                    | 🔒 Admin    |
| GET    | /admin/users                    | 🔒 Admin    |
| POST   | /admin/users/{id}/toggle-active | 🔒 Admin    |

### Messaging
| Method | Endpoint                          | Auth?       |
|--------|----------------------------------|-------------|
| POST   | /messages/conversation           | ✅ Any      |
| POST   | /messages/send                   | ✅ Any      |
| GET    | /messages/conversation/{id}      | ✅ Any      |

---

## 👥 User Roles

| Role    | Description                                      |
|---------|--------------------------------------------------|
| student | Learns skills, takes quizzes, joins sessions     |
| mentor  | Uploads videos, creates sessions, gives feedback |
| admin   | Full control — approve mentors, manage content   |

**Role assignment:**
- Register with `role: "student"` or `role: "mentor"`
- Mentors must apply via `/mentor/apply` and await admin approval
- On approval, user role is promoted to `mentor`

---

## 🎮 Skills Built In

The platform is designed for 7 core skills (add via API or manually):

1. Communication
2. Creativity  
3. Time Management
4. Adaptability
5. Teamwork
6. Critical Thinking
7. Leadership

Seed example via Swagger UI after login.

---

## 🔧 Configuration (.env)

```env
SECRET_KEY=skillseed-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite+aiosqlite:///./skillseed.db
UPLOAD_DIR=uploads
MAX_VIDEO_SIZE_MB=500
MAX_FILE_SIZE_MB=10
```

---

## 🛠️ Tech Stack

| Layer       | Technology              |
|-------------|------------------------|
| API         | FastAPI (Python)        |
| Database    | SQLite (via aiosqlite)  |
| ORM         | SQLAlchemy 2.0 (async)  |
| Auth        | JWT (python-jose)       |
| Passwords   | bcrypt (passlib)        |
| File upload | aiofiles                |
| Live video  | Jitsi Meet (link-based) |

---

## 🚀 Flutter Integration

From your Flutter app:

```dart
// Base URL
const baseUrl = 'http://localhost:8000';

// Login
final res = await http.post(
  Uri.parse('$baseUrl/auth/login'),
  body: jsonEncode({'email': 'user@example.com', 'password': 'pass'}),
  headers: {'Content-Type': 'application/json'},
);
final token = jsonDecode(res.body)['access_token'];

// Authenticated request
final skills = await http.get(
  Uri.parse('$baseUrl/skills'),
  headers: {'Authorization': 'Bearer $token'},
);
```

---

## 📦 Database Tables (53 Total)

Users & Auth (6), Students (3), Mentors (5), Mentor Applications (1),  
Skills (3), Content (4), Quizzes (5), Live Sessions (2),  
Notifications (1), Subscriptions (3), Gamification (4),  
Languages (2), Admin (2), Messaging (3), System (1)
#   s k i l l s e e d 
 
 #   s k i l l s e e d 
