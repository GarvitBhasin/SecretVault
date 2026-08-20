# SecretVault
## Overview
SecretVault is a single-tenant CLI based secrets manager designed to manage and store sensitive data and credentials. The application stores encrypted secrets and provides authenticated users with controlled access to secrets organized into project folders, while enforcing role-based permissions and maintaining an audit log of user actions.

## Features
### Authentication
- Secure login system
- JWT authentication and session management
- Password hashing using ```pwdlib``` 
- Password reset
- Account deletion

### Role Based Access Control (RBAC):
- Consists of three roles: Viewer, Admin and Owner with the following abilities:
    - Viewer: Read-only access
    - Admin: Create, read, and update access
    - Owner: Full access, including deletion and user management
- Permission validation for protected endpoints
- Role-based user management
- Owner-specific administrative controls

### Secrets 
- Encrypted using ```Fernet```
- Carry out CRUD operations based on role
- Organize, create or delete secrets and project folders
- Store metadata such as creator, creation date, updation date etc.

### Audit Logging
- Records user actions performed within the platform
- Tracks the actor, action, affected resource, and timestamp
- Provides a CLI command for viewing system logs

## Tech Stack
### Frontend
- CLI
- Python
- Typer
- Rich
- Requests
### Backend
- Python
- FastAPI
- REST APIs
- SQLAlchemy
- Pydantic
### Database
- PostgreSQL
### Authentication & Security
- JWTs
- python-jose
- pwdlib

## Local Setup
### Clone repository
```
git clone https://github.com/GarvitBhasin/SecretVault/
cd SecretVault
```
### Create virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```
### Install dependencies
```
pip install -r requirements.txt
```

### Database configuration
Create a PostgreSQL database and configure the database connection through an environment variable.

### Configure environment variables
```
DB_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
```

### Run the backend
```
uvicorn backend.main:app --reload
```

### Run the CLI
```
vault init
```

## What I Learnt
I developed a stronger understanding of backend development, authentication, authorization, database design, and API architecture while building SecretVault. This helped me to a lot of new concepts including:
- SQLAlchemy ORM
- Pydantic request and response validation
- CLI development using Typer and Rich
- Encryption using ```Fernet```
- Development of RBAC systems
- JWT sesion management and using ```python-jose``` 

## Future Versions

Future planned updates include:

- Audit log filtering and querying
- Secret versioning and recovery
- Automated tests for authentication, RBAC, and API endpoints
- Rate limiting for authentication and sensitive endpoints

## AI Assistance

A portion of development involved using AI tools including ChatGPT and Gemini to assist with debugging, explaining unfamiliar concepts, exploring alternative implementations, reviewing architectural decisions, and identifying potential issues. The overall application architecture, implementation decisions, code integration, testing, and final verification were performed by me.

## Disclaimer

SecretVault is an educational software project intended to demonstrate concepts related to authentication, authorization, secrets management, backend development, and database systems. It should not be considered production-ready security software without additional security auditing, testing, and hardening.
