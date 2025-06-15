# Database Schema Documentation

## Overview
This document outlines the database schema for the Healthcare Management System. The system uses SQLite as the database engine.

## Entity Relationship Diagram
[Include ERD diagram here]

## Core Models

### User
- Base user model with authentication fields
- Extended with role-based fields and permissions
- Relationships with other models through foreign keys

### Patient
- Personal information
- Medical history
- Emergency contacts
- Linked to appointments and EMR

### Doctor
- Professional information
- Specializations
- Schedule availability
- Linked to appointments and prescriptions

### Appointment
- DateTime fields
- Status tracking
- Patient and doctor references
- Notes and follow-up information

### EMR (Electronic Medical Record)
- Patient history
- Visit records
- Diagnosis information
- Treatment plans
- Attachments and notes

### Prescription
- Medication details
- Dosage information
- Duration
- Doctor and patient references

### Laboratory
- Test types
- Results storage
- Reference ranges
- Patient and doctor references

### Billing
- Service items
- Pricing
- Payment tracking
- Insurance information

## Relationships
- User -> Patient (One-to-One)
- Doctor -> Appointments (One-to-Many)
- Patient -> Appointments (One-to-Many)
- Patient -> EMR (One-to-Many)
- Doctor -> Prescriptions (One-to-Many)

## Indexes
- User email (unique)
- Patient ID
- Appointment datetime
- EMR created date

## Data Integrity
- Foreign key constraints
- Unique constraints
- Check constraints
- Default values
