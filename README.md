# CampusFix

**Smart Campus Complaint & Maintenance Tracker**

CampusFix is a desktop-based complaint and maintenance tracking system developed as a Software Engineering semester project. It provides a structured workflow for students/staff to report campus issues and for administrators to review, assign, prioritize, and resolve them.

## Overview

Campus maintenance complaints are often reported through informal channels such as verbal messages, paper notes, or chat groups. These methods make it difficult to track ownership, priority, location, status, and resolution history. CampusFix converts that process into a simple role-based desktop application with persistent local storage.

## Key Features

- User registration and secure role-based login
- Separate **User** and **Admin** dashboards
- Complaint submission with title, category, location, priority, and description
- Personal complaint history and status tracking
- Admin complaint queue with search and status filtering
- Complaint assignment to staff/technicians
- Status workflow: `Submitted` → `Assigned` → `In Progress` → `Resolved` → `Closed`
- Admin notes and timestamps for complaint updates
- Dashboard statistics for total, open, resolved, and urgent complaints
- Local SQLite persistence
- Automated database tests with Python `unittest`
- Complete SRS, project report, presentation, UML diagrams, and ERD

## Tech Stack

| Area | Technology |
| --- | --- |
| Programming Language | Python 3 |
| Desktop GUI | Tkinter / ttk |
| Database | SQLite |
| Testing | unittest |
| Architecture | Layered desktop architecture |
| SDLC Model | Iterative & Incremental |

The project intentionally uses Python standard-library technologies to keep setup lightweight and suitable for an academic desktop application.

## Screenshots

### User Dashboard

![CampusFix User Dashboard](assets/user%20dashboard.png)

### Admin Dashboard

![CampusFix Admin Dashboard](assets/admin%20dashboard.png)

## System Design

The repository includes the following software engineering diagrams:

- Use Case Diagram
- Class Diagram
- Activity Diagram
- Sequence Diagram
- UML Component Diagram
- Entity Relationship Diagram (ERD)

See [`assets/diagrams`](assets/diagrams) for the complete set.

## Project Structure

```text
CampusFix-GitHub-Ready/
├── assets/
│   ├── diagrams/
│   ├── admin dashboard.png
│   └── user dashboard.png
├── docs/
│   ├── CampusFix Project Report.docx
│   ├── CampusFix Project Report.pdf
│   ├── CampusFix SRS.docx
│   ├── CampusFix SRS.pdf
│   └── CampusFix ppt.pptx
├── src/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   └── main.py
├── tests/
│   └── test_database.py
├── .gitignore
├── README.md
└── run-project.bat
```

## Getting Started

### Prerequisites

- Python 3.x
- Tkinter support for your Python installation

SQLite and `unittest` are part of Python's standard library, so no external Python packages are required for the core project.

### Run the Application

**Option 1 — Windows**

Double-click:

```text
run-project.bat
```

**Option 2 — Terminal**

```bash
cd src
python main.py
```

On first launch, CampusFix automatically creates a local `campusfix.db` database and seeds demo accounts.

## Demo Accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@campusfix.local` | `admin123` |
| User | `student@campusfix.local` | `student123` |

> These accounts are for local academic demonstration only.

## Running Tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

Current automated tests cover:

- Demo user authentication
- User registration and complaint submission
- Admin complaint status/assignment update

## Functional Requirements Covered

CampusFix implements the core requirements defined in the SRS, including registration, authentication, complaint submission, complaint tracking, admin viewing, searching/filtering, assignment, status updates, and dashboard statistics.

## SDLC Approach

The project follows an **Iterative and Incremental Model**. Development was divided into working increments such as database setup, authentication, complaint submission, admin management, dashboard statistics, search/filtering, and testing. This made it possible to test and improve each part before final integration.

## Documentation

The [`docs`](docs) folder contains:

- Software Requirements Specification (SRS)
- Complete Project Report
- Project Presentation

These documents cover requirements, architecture, database design, diagrams, testing, limitations, and future enhancements.

## Team

| Member | Roll Number | Main Responsibility |
| --- | --- | --- |
| Muhammad Azam | Database design, testing support, documentation review |
| Kashif Raza | GUI design, requirements analysis, final integration |

**Course:** Software Engineering  

## Future Enhancements

- Complaint photo attachments
- Email/status notifications
- Web dashboard using Flask or Django
- Technician accounts and task-specific views
- Monthly complaint and response-time analytics
- Role-management interface
- Stronger production-grade password hashing such as Argon2 or bcrypt

## Security Note

This repository is an academic project. The current implementation uses SHA-256 hashing for demonstration purposes. A production system should use a password-specific, salted, adaptive hashing algorithm such as Argon2 or bcrypt and should apply additional security controls.

## License

This project was created for academic/educational use. If the team wants to release it as open-source software, an explicit license (for example, MIT) can be added after all contributors agree.
