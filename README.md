# Hospital Inter-Department Consultation System

A modern web-based consultation management system for hospitals, enabling doctors to create, track, and respond to consultation requests between departments.

## Features

- **User Authentication**: Secure JWT-based authentication
- **Department Management**: Support for multiple hospital departments (Medicine, Surgery, Cardiology, Radiology, Pathology)
- **Patient Management**: Simple patient information tracking
- **Consultation Requests**: Create and manage consultation requests with priority levels
- **Real-time Comments**: Add comments and replies to consultations
- **Status Tracking**: Track consultation status (Pending, In Progress, Completed, Cancelled)
- **Role-based Views**: 
  - View incoming consultations (to your department)
  - View outgoing consultations (from your department)

## Tech Stack

### Backend
- Python 3.12
- Django 5.2
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios

### Infrastructure
- Docker & Docker Compose
- Nginx (for frontend serving)
- PostgreSQL 16

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd onlineconsult
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start the application:
```bash
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

### Default Credentials

The system comes pre-seeded with test users:

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Doctor Users:**
- Username: `doctor_medicine` | Password: `doctor123` (Medicine Department)
- Username: `doctor_surgery` | Password: `doctor123` (Surgery Department)
- Username: `doctor_cardiology` | Password: `doctor123` (Cardiology Department)
- Username: `doctor_radiology` | Password: `doctor123` (Radiology Department)
- Username: `doctor_pathology` | Password: `doctor123` (Pathology Department)

## User Workflows

### 1. Login
- Navigate to http://localhost:3000
- Enter username and password
- Click "Sign in"

### 2. View Consultations
- **Incoming Consults**: View consultation requests sent to your department
- **Outgoing Consults**: View consultation requests you or your department sent

### 3. Create a New Consultation
1. Click "New Consult" button
2. Fill in patient information:
   - Hospital ID/MRN
   - Patient name, age, gender
   - Bed/Ward information (optional)
3. Fill in consultation details:
   - Select target department
   - Choose priority (Routine, Urgent, STAT/Emergency)
   - Enter clinical summary
   - Enter specific consultation question
4. Click "Create Consult"

### 4. Respond to a Consultation
1. Click on a consultation from the list
2. Review patient and consultation details
3. Add comments/replies in the comments section
4. Update the status as needed:
   - **Pending**: Initial status
   - **In Progress**: Actively working on the consultation
   - **Completed**: Consultation is finished
   - **Cancelled**: Consultation is no longer needed

## Development

### Running Backend Locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Running Frontend Locally (without Docker)

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

**Backend Tests:**
```bash
cd backend
python manage.py test
```

## API Documentation

### Authentication
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token

### Departments
- `GET /api/departments/` - List all departments

### Patients
- `GET /api/patients/` - List patients (with search)
- `POST /api/patients/` - Create new patient
- `GET /api/patients/{id}/` - Get patient details

### Consultations
- `GET /api/consults/` - List consultations (with filters)
  - Query params: `role=incoming|outgoing`, `status=pending|in_progress|completed|cancelled`
- `POST /api/consults/` - Create new consultation
- `GET /api/consults/{id}/` - Get consultation details
- `POST /api/consults/{id}/add_comment/` - Add comment to consultation
- `GET /api/consults/{id}/comments/` - Get consultation comments
- `PATCH /api/consults/{id}/update_status/` - Update consultation status

## Project Structure

```
onlineconsult/
├── backend/
│   ├── consults/              # Main Django app
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # URL routing
│   │   ├── admin.py           # Django admin config
│   │   ├── tests.py           # Unit tests
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py  # Data seeding command
│   ├── core/                  # Django project settings
│   │   ├── settings.py
│   │   └── urls.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts (Auth)
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Security Notes

- Change the `DJANGO_SECRET_KEY` in production
- Use strong passwords for database and admin users
- Set `DJANGO_DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS` in production
- Use HTTPS in production
- Implement proper CORS settings for production

## License

This project is for educational and demonstration purposes.
