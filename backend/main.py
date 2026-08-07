from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, func
from pwdlib import PasswordHash
from dotenv import load_dotenv
from backend.security import *
from backend.models import *
import re, os


load_dotenv()
app = FastAPI()
SessionLocal = sessionmaker(bind=engine)
password_hash = PasswordHash.recommended()

# AUTH

@app.post("/register", status_code=201)
def register(data: RegisterRequest):

    # Check email validity
    email_valid = bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", data.email))

    if not email_valid:
        raise_error(400, "Invalid email.")

    # Check password pairs
    if data.confirm != data.password:
        raise_error(400, "Passwords do not match.")
        

    # Check password strength
    has_char = any(char.isalpha() for char in data.password)
    has_digit = any(char.isdigit() for char in data.password)
    has_symbol = any(not char.isalnum() for char in data.password)
    is_long = len(data.password) > 8

    if not (has_char and has_digit and has_symbol and is_long):
        raise_error(422, "Password must have at least one character, digit, symbol and must be more than 8 characters long.")

    try:
        session = SessionLocal()

        # Check for duplicate email or username
        existing_email = session.execute(
            select(Users).where(Users.email == data.email)
        ).scalar_one_or_none()

        existing_username = session.execute(
            select(Users).where(Users.username == data.username)
        ).scalar_one_or_none()

        if existing_email:
            raise_error(409, "Email already registered.") 
        if existing_username:
            raise_error(409, "Username taken.") 

        # Hash password
        hashed_pass = password_hash.hash(data.password)

        # Create user
        user = Users(
            username = data.username,
            email = data.email,
            password_hash = hashed_pass,
        )
    
        session.add(user)
        session.commit()

        # Return token and message
        id = session.execute(select(Users.id).where(Users.email == data.email)).scalar_one()
        print(id)
        token = encode_token({ "sub": str(id) })
                
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Account created."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.post("/login")
def login(data: LoginRequest):

    try:
        session = SessionLocal()

        # find user in db with corelating hash and id
        result = session.execute(select(Users.password_hash, Users.id).where(Users.email == data.email)).first()

        if result is None:
            raise_error(401, "Incorrect email or password.")

        stored_hash, id = result

        # Check if password is correct
        is_valid = password_hash.verify(data.password, stored_hash)

        if not is_valid:
            raise_error(401, "Incorrect email or password.")

        # Return token and message
        token = encode_token({"sub": str(id)})
        
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Logged in."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/me")
def me(data: TokenRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        result = session.execute(select(Users.username, Users.email).where(Users.id == id)).first()

        if result is None:
            raise_error(404, "User not found.")

        username, email = result

        return {
            "message": f"Loaded user details.\nUsername: {username}\nEmail: {email}",
        }

    finally:
        session.close()

@app.post("/delete")
def delete_user(data: TokenRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        result = session.execute(delete(Users).where(Users.id == id))
        session.commit()

        if result.rowcount == 0:
            raise_error(404, "User not found.")

        return {
            "message": "Account deleted."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# PROJECTS

@app.post("/create-project", status_code=201)
def create_project(data: CreateRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        project = Projects(
            name = data.name,
            creator_id = id
        )

        session.add(project)
        session.commit()

        return {
            "message": "Project created."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/list-projects")
def list_projects(data: TokenRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        projects = session.execute(
            select(Projects.id, Projects.name, Users.username)
                .join(Users, Projects.creator_id == Users.id)
                .order_by(Projects.id.asc())
        ).all()
  
        secrets_sum = session.execute(
            select(Projects.id, func.count(Secrets.project_id))
                .select_from(Projects)
                .outerjoin(Secrets, Projects.id == Secrets.project_id)
                .group_by(Projects.id).order_by(Projects.id.asc())
        ).all()

        if len(projects) == 0:
            raise_error(404, "No projects found.")

        project_list = []

        for index, project in enumerate(projects):

            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "creator": project.username,
                "secrets": str(secrets_sum[index][1])
            })

        return {
            "list": project_list,
            "message": "Loaded projects."
        }

    finally:
        session.close()

@app.delete("/delete-project")
def delete_project(data: IDRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        project = session.execute(delete(Projects).where(Projects.id == int(data.id)))
        session.commit()
        
        if project.rowcount == 0:
            raise_error(404, "Project not found.")

        return {
            "message": "Project deleted."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.patch("/edit-project")
def edit_project(data: EditRequest):

    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        result = session.execute(update(Projects)
            .where(Projects.id == int(data.id))
            .values(name = data.name)
        )
        session.commit()

        if result.rowcount == 0:
            raise_error(404, "Project not found.")

        return {
            "message": "Project edited."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/open-project")
def open_project(data: IDRequest):
    try:
        session = SessionLocal()

        id = verify_user(data.token, session)

        secrets = session.execute(
            select(
                Secrets, Users.username
            )
            .where(Secrets.project_id == int(data.id))
            .join(Users, Users.id == Secrets.creator_id)
            .order_by(Secrets.updated_at.desc())
        ).all()

        if len(secrets) == 0:
            raise_error(404, "No secrets found.")

        secrets_list = []
        
        for secret, username in secrets:

            secrets_list.append({
                "id": str(secret.id),
                "name": secret.name,
                "value": secret.value,
                "creator": username,
                "created_at": str(secret.created_at),
                "updated_at": str(secret.updated_at),
            })

        return {
            "secrets": secrets_list,
            "message": "Loaded secrets."
        }

    finally:
        session.close()

# SECRETS

@app.get("/open-project")
def open_project(data: IDRequest):