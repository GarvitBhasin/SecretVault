from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, func
from pwdlib import PasswordHash
from dotenv import load_dotenv
from backend.security import *
from backend.models import *
from backend.helpers import *
from sqlalchemy.exc import IntegrityError
import os

load_dotenv()
app = FastAPI()
SessionLocal = sessionmaker(bind=engine)
password_hash = PasswordHash.recommended()

# AUTH

@app.post("/register", status_code=201)
def register(data: RegisterRequest):

    # Check email validity
    if not email_valid(data.email):
        raise_error(400, "Invalid email.")

    # Check password pairs
    if data.confirm != data.password:
        raise_error(400, "Passwords do not match.")
        
    # Check password strength
    if not password_strong(data.password):
        raise_error(422, "Password must have at least one character, digit, symbol and must be more than 8 characters long.")

    try:
        session = SessionLocal()

        # Hash password
        hashed_pass = password_hash.hash(data.password)

        # Create user object and add to db
        user = Users(
            username = data.username,
            email = data.email,
            password_hash = hashed_pass,
        )
        session.add(user)
        session.commit()

        # Return token and message
        token = encode_token({ "sub": str(user.id) })

        print(token)
                
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Created account."
        }
    
    except Exception:
        session.rollback()
        raise

    except IntegrityError as error:
        session.rollback()

        if "users_email_key" in str(error):
            raise_error(409, "Email already registered.")

        if "users_username_key" in str(error):
            raise_error(409, "Username taken.")

        raise

    finally:
        session.close()

@app.post("/login")
def login(data: LoginRequest):

    try:
        session = SessionLocal()

        # Find user in db
        result = session.execute(
            select(Users.password_hash, Users.id).where(Users.email == data.email)
        ).first()

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

        user_id = verify_user(data.token, session)

        # Find user in db raise error if not found
        result = session.execute(
            select(Users.username, Users.email).where(Users.id == user_id)
        ).first()

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

        user_id = verify_user(data.token, session)

        # Delete user
        result = session.execute(
            delete(Users).where(Users.id == user_id)
        )
        session.commit()

        # Check if user found and return message
        if result.rowcount == 0:
            raise_error(404, "User not found.")

        return {
            "message": "Deleted account."
        }
    
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# PROJECTS

@app.post("/create-project", status_code=201)
def create_project(data: CreateProjectRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Create project object and add to db
        project = Projects(
            name = data.name,
            creator_id = user_id,
            created_at = now(),
            updated_at = now()
        )

        session.add(project)
        session.commit()

        return {
            "message": "Created project."
        }
    
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.delete("/delete-project")
def delete_project(data: IDRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        project = session.execute(
            delete(Projects).where(Projects.id == data.id
        ))

        session.commit()
        
        if project.rowcount == 0:
            raise_error(404, "Project not found.")

        return {
            "message": "Deleted project."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.patch("/edit-project")
def edit_project(data: EditProjectRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        result = session.execute(
            update(Projects)
            .where(Projects.id == data.id)
            .values(
                name = data.name,
                updated_at = now()
            )
        )

        # Update project last updated column
        update_project_timestamp(session, data)

        session.commit()

        if result.rowcount == 0:
            raise_error(404, "Project not found.")

        return {
            "message": "Edited project."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/list-project")
def list_project(data: TokenRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Join project id, project name, and project creator's username
        projects = session.execute(
            select(Projects.id, Projects.name, Users.username, Projects.created_at, Projects.updated_at)
                .join(Users, Projects.creator_id == Users.id)
                .order_by(Projects.id.asc())
        ).all()

        # Calculate sum of secrets for each project
        secrets_sum = session.execute(
            select(Projects.id, func.count(Secrets.project_id))
                .select_from(Projects)
                .outerjoin(Secrets, Projects.id == Secrets.project_id)
                .group_by(Projects.id)
                .order_by(Projects.id.asc())
        ).all()
        
        if len(projects) == 0:
            raise_error(404, "No projects found.")

        project_list = []

        # Create array of project dicts (used to display table on cli)
        for index, project in enumerate(projects):

            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "creator": project.username,
                "secrets": str(secrets_sum[index][1]),
                "created_at": str(project.created_at.replace(microsecond=0)),
                "updated_at": str(project.updated_at.replace(microsecond=0))
            })

        return {
            "projects": project_list,
            "message": "Loaded projects."
        }

    finally:
        session.close()

# SECRETS

@app.post("/create-secret")
def create_secret(data: SecretRequest):
    try:
        session = SessionLocal()

        creator_id = verify_user(data.token, session)

        # Create secret object and add to db
        secret = Secrets(
            name = data.name,
            value = data.value,
            description = data.description,
            project_id = data.id,
            creator_id = creator_id,
            created_at = now(),
            updated_at = now()
        )

        session.add(secret)

        # Update project last updated column
        update_project_timestamp(session, data)

        session.commit()

        return {
            "message": "Created secret."
        }      

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.delete("/delete-secret")
def delete_secret(data: IDRequest):

    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Delete user
        secret = session.execute(
            delete(Secrets)
            .where(Secrets.id == data.id)
        )

        # Update project last updated column
        update_project_timestamp(session, data)

        session.commit()
        
        if secret.rowcount == 0:
            raise_error(404, "Secret not found.")

        return {
            "message": "Deleted secret."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.patch("/edit-secret")
def edit_secret(data: SecretRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Execute edit query
        result = session.execute(
            update(Secrets)
            .where(Secrets.id == data.id)
            .values(
                name = data.name, 
                value = data.value, 
                description = data.description,
                updated_at = now()
            )
        )

        # Update project last updated column
        update_project_timestamp(session, data)

        session.commit()

        if result.rowcount == 0:
            raise_error(404, "Secret not found.")

        return {
            "message": "Edited secret."
        }

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/list-secret")
def list_secret(data: IDRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Check if project exists
        project_found = session.execute(
            select(Projects)
            .where(Projects.id == data.id)
        ).first()

        if not project_found:
            raise_error(404, "Project not found.")

        # Join Secrets with creator's corrosponding username
        secrets = session.execute(
            select(
                Secrets, Users.username
            )
            .where(Secrets.project_id == data.id)
            .join(Users, Users.id == Secrets.creator_id)
            .order_by(Secrets.id.asc())
        ).all()

        if len(secrets) == 0:
            raise_error(404, "No secrets found.")

        secrets_list = []

        # Create array of secret dicts (used to display table on cli)
        for secret, username in secrets:

            secrets_list.append({
                "id": str(secret.id),
                "name": secret.name,
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

@app.get("/get-secret")
def get_secret(data: IDRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Find secret
        secret = session.execute(
            select(Secrets)
            .where(Secrets.id == data.id)
        ).scalar_one_or_none()

        if secret is None:
            raise_error(404, "Secret not found.")

        # Find creator    
        creator = session.execute(
            select(Users.username)
            .where(Users.id == secret.creator_id)
        ).scalar_one()

        return {
            "secret": f"Name: {secret.name}\nValue: {secret.value}\nDescription: {secret.description}\nCreator: {creator}\nCreated At: {secret.created_at}\nLast Updated: {secret.updated_at}",
            "message": "Loaded secret."
        }
    
    finally:
        session.close()