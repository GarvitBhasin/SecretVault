from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update, func
from pwdlib import PasswordHash
from backend.security import *
from backend.database import *
from backend.helpers import *
from sqlalchemy.exc import IntegrityError

app = FastAPI()
SessionLocal = sessionmaker(bind=engine)

# AUTH

@app.post("/add-user", status_code=201)
def add_user(data: RegisterRequest):

    # Check email validity, password pairs, role validity, and password strenght
    if not email_valid(data.email):
        raise_error(400, "Invalid email.")

    if data.confirm != data.password:
        raise_error(400, "Passwords do not match.")

    if data.role not in range(1, 4):
        raise_error(400, "Invalid role.")    
    
    if not password_strong(data.password):
        raise_error(422, "Password must have at least one character, digit, symbol and must be more than 8 characters long.")

    # Hash password
    hashed_pass = hash_password(data.password)

    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)
        validate_user(session, user_id, Role.ADMIN)

        # Create user object and add to db
        user = Users(
            username = data.username,
            email = data.email,
            password_hash = hashed_pass,
            role=data.role
        )
    
        session.add(user)
        session.flush()

        add_log(session, user.id, Action.CREATE, Asset.ACCOUNT, user.id)

        session.commit()
                
        return {
            "message": "Created account."
        }

    # Return error if email/username already exist
    except IntegrityError as error:
        session.rollback()

        if "users_email_key" in str(error):
            raise_error(409, "Email already registered.")

        if "users_username_key" in str(error):
            raise_error(409, "Username taken.")

        raise
        
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

@app.post("/login")
def login(data: LoginRequest):
    try:
        session = SessionLocal()

        # Find user in db
        result = session.execute(
            select(Users.id, Users.password_hash)
            .where(Users.email == data.email)
        ).first()

        if result is None:
            raise_error(401, "Incorrect email or password.")

        user_id, stored_hash = result

        # Check if password matches
        if not verify_password(data.password, stored_hash):
            raise_error(401, "Incorrect email or password.")

        # Return token and message
        token = encode_token({"sub": str(user_id)})
        
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
        username, email, role = session.execute(
            select(Users.username, Users.email, Users.role)
            .where(Users.id == user_id)
        ).first()

        return {
            "message": f"Loaded user details.\nUsername: {username}\nEmail: {email}\nRole: {role}",
        }

    finally:
        session.close()

@app.delete("/delete-user")
def delete_user(data: TokenRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        # Delete user if found
        result = session.execute(
            delete(Users)
            .where(Users.id == user_id)
        )

        add_log(session, user_id, Action.DELETE, Asset.ACCOUNT, user_id)

        session.commit()

        return {
            "message": "Deleted account."
        }
    
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

@app.get("/list-user")
def list_users(data: TokenRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        users = session.execute(
            select(Users)
        ).scalars().all()

        users_arr = []

        for user in users:
            users_arr.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            })

        return {
            "users": users_arr,
            "message": "Loaded users."
        }
    
    finally:
        session.close()

# PROJECTS

@app.post("/create-project", status_code=201)
def create_project(data: CreateProjectRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)
        validate_user(session, user_id, Role.ADMIN)

        # Create project object and add to db
        current_time = now()
        project = Projects(
            name = data.name,
            creator_id = user_id,
            created_at = current_time,
            updated_at = current_time
        )

        session.add(project)
        session.flush()

        add_log(session, user_id, Action.CREATE, Asset.PROJECT, project.id)

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
        validate_user(session, user_id, Role.OWNER)

        project = session.execute(
            delete(Projects)
            .where(Projects.id == data.id)
        )

        if project.rowcount == 0:
            raise_error(404, "Project not found.")

        add_log(session, user_id, Action.DELETE, Asset.PROJECT, data.id)

        session.commit()
        
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
        validate_user(session, user_id, Role.ADMIN)

        result = session.execute(
            update(Projects)
            .where(Projects.id == data.id)
            .values(
                name = data.name,
                updated_at = now()
            )
        )

        if result.rowcount == 0:
            raise_error(404, "Project not found.")

        add_log(session, user_id, Action.UPDATE, Asset.PROJECT, data.id)

        session.commit()

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

        if not projects:
            raise_error(404, "No projects found.")

        # Calculate sum of secrets for each project
        secrets_sum = session.execute(
            select(func.count(Secrets.project_id))
                .select_from(Projects)
                .outerjoin(Secrets, Projects.id == Secrets.project_id)
                .group_by(Projects.id)
                .order_by(Projects.id.asc())
        ).all()
        
        project_list = []

        # Create array of project dicts (used to display table on cli)
        for index, project in enumerate(projects):

            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "creator": project.username,
                "secrets": str(secrets_sum[index][0]),
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

@app.post("/create-secret", status_code=201)
def create_secret(data: SecretRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)
        validate_user(session, user_id, Role.ADMIN)

        project = session.execute(
            select(Projects)
            .where(Projects.id == data.id)
        ).scalar_one_or_none()

        if project is None:
            raise_error(404, "Project not found.")

        # Create secret object and add to db
        current_time = now()
        secret = Secrets(
            name = data.name,
            value = encrypt(data.value),
            description = data.description,
            project_id = data.id,
            creator_id = user_id,
            created_at = current_time,
            updated_at = current_time
        )

        session.add(secret)
        session.flush()

        # Update project last updated column
        update_project_timestamp(session, data.id)

        add_log(session, user_id, Action.CREATE, Asset.SECRET, secret.id)

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
        validate_user(session, user_id, Role.OWNER)

        project_id = find_project(session, data.id)
        
        # Delete secret
        secret = session.execute(
            delete(Secrets)
            .where(Secrets.id == data.id)
        )

        if secret.rowcount == 0:
            raise_error(404, "Secret not found.")

        # Update project's updated at column
        update_project_timestamp(session, project_id)

        add_log(session, user_id, Action.DELETE, Asset.SECRET, data.id)

        session.commit()

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
        validate_user(session, user_id, Role.ADMIN)

        # Execute edit query
        result = session.execute(
            update(Secrets)
            .where(Secrets.id == data.id)
            .values(
                name = data.name, 
                value = encrypt(data.value), 
                description = data.description if data.description else None,
                updated_at = now()
            )
        )

        if result.rowcount == 0:
            raise_error(404, "Secret not found.")

        # Find project id and update its updated at column
        project_id = find_project(session, data.id)
        update_project_timestamp(session, project_id)

        add_log(session, user_id, Action.UPDATE, Asset.SECRET, data.id)

        session.commit()

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
            .outerjoin(Users, Users.id == Secrets.creator_id)
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
                "creator": username if username else "Deleted user",
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
        result = session.execute(
            select(Secrets, Users.username)
            .where(Secrets.id == data.id)
            .outerjoin(Users, Users.id == Secrets.creator_id)
        ).first()

        if result is None:
            raise_error(404, "Secret not found.")

        secret, username = result

        add_log(session, user_id, Action.READ, Asset.SECRET, data.id)

        return {
            "secret": f"Name: {secret.name}\nValue: {decrypt(secret.value)}\nDescription: {secret.description}\nCreator: {username if username else "Deleted user"}\nCreated At: {secret.created_at}\nLast Updated: {secret.updated_at}",
            "message": "Loaded secret."
        }
    
    finally:
        session.close()

# LOGS

@app.get("/logs")
def logs(data: TokenRequest):
    try:
        session = SessionLocal()

        user_id = verify_user(data.token, session)

        logs_obj = session.execute(
            select(Logs, Users.username)
            .outerjoin(Users, Logs.actor_id == Users.id)
        ).all()

        logs = []

        for log, username in logs_obj:
            logs.append({
                "id": str(log.id),
                "actor": username if username else "Deleted User",
                "action": log.action,
                "asset_type": log.asset_type,
                "asset_id": str(log.asset_id),
                "action_date": str(log.action_date)
            })

        return {
            "logs": logs,
            "message": "Loaded logs."
        }
    
    finally:
        session.close()