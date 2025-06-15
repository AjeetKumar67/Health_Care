# API Documentation

## Base URL
All API endpoints are relative to: `http://localhost:8000/`

## Authentication

### Register User
```http
POST /auth/register/
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "PATIENT"
}
```
**Response:** `201 Created`

### Login
```http
POST /auth/login/
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
**Response:**
```json
{
  "access": "access_token",
  "refresh": "refresh_token"
}
```

### Refresh Token
```http
POST /auth/token/refresh/
```
**Request Body:**
```json
{
  "refresh": "refresh_token"
}
```

## Patient Management

### Create Patient Profile
```http
POST /api/patients/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "date_of_birth": "1990-01-01",
  "blood_group": "A+",
  "gender": "M",
  "address": "123 Main St",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567890",
  "allergies": "None"
}
```

### Get Patient Medical History
```http
GET /api/patients/{id}/medical_history/
```
**Headers:**
```
Authorization: Bearer <access_token>
```

## Appointments

### List Doctors
```http
GET /api/doctors/
```
**Headers:**
```
Authorization: Bearer <access_token>
```

### Create Appointment
```http
POST /api/appointments/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "doctor": 1,
  "appointment_date": "2025-06-14",
  "appointment_time": "10:00",
  "reason": "Regular checkup"
}
```

## Hospital Management System (HMS)

### EMR Management

#### Create EMR
```http
POST /api/emr/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "patient": 1,
  "symptoms": "Fever, headache",
  "diagnosis": "Common cold",
  "notes": "Rest and hydration recommended"
}
```

### Laboratory

#### Create Lab Test
```http
POST /api/lab-tests/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "patient": 1,
  "test_name": "Blood Test",
  "test_date": "2025-06-14",
  "notes": "Fasting required"
}
```

### Billing

#### Create Bill
```http
POST /api/bills/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "patient": 1,
  "consultation_fee": 100.00,
  "medicine_charges": 50.00,
  "lab_charges": 200.00,
  "other_charges": 0.00,
  "discount": 0.00
}
```

### Emergency Services

#### List Available Vehicles
```http
GET /api/emergency-services/available_vehicles/
```
**Headers:**
```
Authorization: Bearer <access_token>
```

#### Create Emergency Call
```http
POST /api/emergency-calls/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "caller_name": "John Smith",
  "caller_phone": "+1234567890",
  "location": "456 Emergency St",
  "description": "Car accident victim",
  "priority": "HIGH"
}
```

### Inventory Management

#### Add Inventory Item
```http
POST /api/inventory/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "name": "Surgical Masks",
  "category": "SUPPLIES",
  "description": "3-ply surgical masks",
  "unit": "boxes",
  "quantity": 100,
  "reorder_level": 20,
  "unit_price": 15.99,
  "supplier": "Medical Supplies Co."
}
```

### Support System
#### Create Support Ticket
```http
POST /api/support-tickets/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "title": "Equipment Malfunction",
  "description": "X-ray machine not working properly",
  "priority": "HIGH"
}
```

### Staff Management
#### Record Attendance
```http
POST /api/attendance/
```
**Headers:**
```
Authorization: Bearer <access_token>
```
**Request Body:**
```json
{
  "staff": 1,
  "date": "2025-06-13",
  "time_in": "09:00",
  "status": "PRESENT"
}
```

## Common Response Codes

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Error Response Format
```json
{
  "error": "Error message",
  "details": {
    "field": ["Error details"]
  }
}
```

## Pagination
API endpoints that return lists support pagination with the following query parameters:
- `page`: Page number
- `page_size`: Number of items per page

Example:
```http
GET /api/patients/?page=1&page_size=10
```

## Filtering and Searching
Many endpoints support filtering and searching using query parameters:
```http
GET /api/appointments/?status=SCHEDULED
GET /api/patients/?search=john
```

## File Uploads
For endpoints that accept file uploads (like documents):
- Use multipart/form-data
- Maximum file size: 10MB
- Supported formats: PDF, JPG, PNG, DOCX
