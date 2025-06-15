# Healthcare Management System

## Overview
A comprehensive Healthcare Management System built with Django Rest Framework that handles patient management, appointments, EMR, billing, and more. The system is designed to streamline healthcare facility operations with role-based access control and comprehensive features.

## Features

### 1. Authentication System
- JWT-based authentication
- Role-based access control (Admin, Doctor, Nurse, Receptionist, Patient)
- Password management with reset functionality
- User profile management

### 2. Patient Management
- Complete patient profiles
- Medical history tracking
- Document management
- Emergency contact information
- Allergy tracking

### 3. Appointment System
- Doctor profile management
- Availability scheduling
- Appointment booking and tracking
- Status management (Scheduled, Completed, Cancelled, No-show)

### 4. Hospital Management System (HMS)

#### a. Electronic Medical Records (EMR)
- Patient visit tracking
- Diagnosis management
- Treatment notes
- Medical history

#### b. Prescription Management
- Medicine prescription
- Dosage tracking
- Duration management
- Prescription history

#### c. Laboratory System
- Test ordering
- Results management
- File attachments
- Status tracking

#### d. Pharmacy Management
- Medicine inventory
- Stock tracking
- Reorder management
- Pricing management

#### e. Billing System
- Consultation fees
- Medicine charges
- Laboratory charges
- Discount management
- Payment tracking

#### f. Infrastructure Management
- Room management
- Occupancy tracking
- Rate management
- Room types (General, Private, ICU, OT)

#### g. Emergency Services
- Ambulance management
- Emergency call handling
- Location tracking
- Priority-based dispatch

#### h. Inventory Management
- Medical supplies tracking
- Equipment management
- Stock level monitoring
- Supplier management

#### i. Support System
- Ticket management
- Priority levels
- Status tracking
- Response management

#### j. Staff Management
- Attendance tracking
- Leave management
- Schedule management
- Performance tracking

## Technical Stack

### Backend
- Django Rest Framework
- SQLite Database
- JWT Authentication
- Cors Headers

### API Documentation
- RESTful API architecture
- Detailed Postman collection
- Environment configuration

## Getting Started

### Prerequisites
- Python 3.12+
- Django 5.2+
- Django Rest Framework
- Other dependencies in requirements.txt

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd healthcare
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a .env file in the root directory with:
```env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Run the server
```bash
python manage.py runserver
```

### API Testing
1. Import the Postman collection from `/Postman/collection.json`
2. Import the environment from `/Postman/environment.json`
3. Set up environment variables
4. Test the endpoints

## Project Structure
```
healthcare/
├── Auth/                   # Authentication app
├── appointments/           # Appointments management
├── documents/             # Project documentation
├── healthcare/            # Project settings
├── HMS/                   # Hospital Management System
├── patients/              # Patient management
└── Postman/               # API collection and environment
```

## Role-Based Access Control

### Admin
- Full system access
- User management
- System configuration
- Report generation

### Doctor
- Patient records access
- Appointment management
- Prescription creation
- Lab test ordering

### Nurse
- Patient vital recording
- Medicine administration
- Patient care notes
- Inventory access

### Receptionist
- Appointment scheduling
- Patient registration
- Bill generation
- Basic patient info access

### Patient
- Personal record access
- Appointment booking
- Medical history view
- Document upload

## API Endpoints

### Authentication
- POST /auth/register/
- POST /auth/login/
- POST /auth/token/refresh/
- PUT /auth/change-password/
- PUT /auth/update-profile/
- POST /auth/request-reset-password/
- POST /auth/reset-password/
- POST /auth/logout/

### Patient Management
- GET /api/patients/
- POST /api/patients/
- GET /api/patients/{id}/
- GET /api/patients/{id}/medical_history/
- POST /api/medical-histories/
- POST /api/documents/

### Appointments
- GET /api/doctors/
- GET /api/doctor-availability/
- POST /api/appointments/
- POST /api/appointments/{id}/cancel/
- POST /api/appointments/{id}/complete/

### HMS
- EMR endpoints
- Lab test endpoints
- Billing endpoints
- Room management endpoints
- Emergency service endpoints
- Inventory endpoints
- Support ticket endpoints
- Staff management endpoints

## Security Measures
- JWT token authentication
- Role-based permissions
- Password encryption
- Token blacklisting
- Session management
- CORS configuration

## Data Models
Detailed documentation of database models and relationships is available in each app's models.py file.

## Contributing
Guidelines for contributing to the project:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License

## Support
For support, contact [support-email]
