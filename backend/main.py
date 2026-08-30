from fastapi import FastAPI, Depends

from backend.database import *
from backend.helpers import *
from backend.requests import *
from backend.dependencies import get_db, get_user_id, require_role

from backend.services.auth.initialize import initialize_vault
from backend.services.auth.login import login_user
from backend.services.auth.delete_self import delete_self
from backend.services.auth.reset_password import reset_password

from backend.services.users.create_user import create_user
from backend.services.users.delete_user import delete_user
from backend.services.users.edit_user import edit_user
from backend.services.users.list_users import list_users

from backend.services.projects.create_project import create_project
from backend.services.projects.delete_project import delete_project
from backend.services.projects.edit_project import edit_project
from backend.services.projects.list_projects import list_projects

from backend.services.secrets.create_secret import create_secret
from backend.services.secrets.delete_secret import delete_secret
from backend.services.secrets.edit_secret import edit_secret
from backend.services.secrets.list_secrets import list_secrets
from backend.services.secrets.get_secret import get_secret

from backend.services.logs.list_logs import list_logs

from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import Session

app = FastAPI()

# INIT

@app.post("/init", status_code=201)
def init(
    data: InitRequest, 
    session: Session = Depends(get_db)
):

    initialize_vault(
        data.username, 
        data.email, 
        data.password, 
        data.confirm, 
        session
    )

    session.commit()

    return {
        "message": "Owner account created. You can now log in with your credentials."
    }

# AUTH

@app.post("/login")
def login(
    data: LoginRequest, 
    session: Session = Depends(get_db)
):

    token = login_user(
        data.email, 
        data.password, 
        session
    )
    
    return {
        "token": token,
        "token_type": "bearer",
        "message": "Logged in."
    }

@app.get("/me")
def me(
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    # Find user in db
    username, email, role = session.execute(
        select(Users.username, Users.email, Users.role)
        .where(Users.id == user_id)
    ).first()

    return {
        "message": f"Loaded user details.\nUsername: {username}\nEmail: {email}\nRole: {role.lower()}",
    }

@app.delete("/delete-self")
def delete(
    data: DeleteSelfRequest, 
    session: Session = Depends(get_db), 
    user_id: int = Depends(get_user_id)
):

    delete_self(
        data.password, 
        user_id, 
        session
    )

    session.commit()

    return {
        "message": "Deleted account."
    }

@app.patch("/reset-password")
def reset_pass(
    data: ResetPasswordRequest, 
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    reset_password(
        data.password,
        data.confirm, 
        user_id, 
        session
    )

    session.commit()

    return {
        "message": "Password reset successfully."
    }

# USER

@app.post("/create-user", status_code=201)
def create_usr(
    data: AddUserRequest, 
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.ADMIN))
):

    create_user(
        data.username, 
        data.email, 
        data.password, 
        data.confirm, 
        data.role, 
        user_id, 
        self_role, 
        session
    )

    session.commit()
            
    return {
        "message": "Created account."
    }

@app.delete("/delete-user")
def delete_usr(
    data: ResourceIDRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.OWNER))
):

    delete_user(
        data.id,
        user_id,
        session
    )    

    session.commit()

    return {
        "message": "Account deleted successfully."
    }

@app.patch("/edit-user")
def edit_user(
    data: EditUserRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.OWNER))
):

    edit_user(
        data.id,
        data.role,
        self_role,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Updated user role."
    }

@app.get("/list-users")
def list_usrs(
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    users = list_users(session)

    return {
        "users": users,
        "message": "Loaded users."
    }

# PROJECTS

@app.post("/create-project", status_code=201)
def create_proj(
    data: CreateProjectRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.ADMIN))
):

    create_project(
        data.name,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Created project."
    }

@app.delete("/delete-project")
def delete_proj(
    data: ResourceIDRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.OWNER))
):

    delete_project(
        data.id,
        user_id,
        session
    )

    session.commit()
    
    return {
        "message": "Deleted project."
    }

@app.patch("/edit-project")
def edit_proj(
    data: EditProjectRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.ADMIN))
):

    edit_project(
        data.name,
        data.id,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Edited project."
    }


@app.get("/list-project")
def list_proj(
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    projects = list_projects(session)

    return {
        "projects": projects,
        "message": "Loaded projects."
    }

# SECRETS

@app.post("/create-secret", status_code=201)
def create_sec(
    data: SecretInfoRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.ADMIN))
):

    create_secret(
        data.id,
        data.name,
        data.description,
        data.value,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Created secret."
    }

@app.delete("/delete-secret")
def delete_sec(
    data: ResourceIDRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.OWNER))
):

    delete_secret(
        data.id,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Deleted secret."
    }

@app.patch("/edit-secret")
def edit_sec(
    data: SecretInfoRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
    self_role: Role = Depends(require_role(Role.ADMIN))
):

    edit_secret(
        data.id,
        data.name,
        data.value,
        data.description,
        user_id,
        session
    )

    session.commit()

    return {
        "message": "Edited secret."
    }

@app.get("/list-secret")
def list_sec(
    data: ResourceIDRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    secrets = list_secrets(session)

    return {
        "secrets": secrets,
        "message": "Loaded secrets."
    }

@app.get("/get-secret")
def get_secret(
    data: ResourceIDRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    secret = get_secret(
        data.id,
        user_id,
        session
    )

    session.commit()

    return {
        "secret": secret,
        "message": "Loaded secret."
    }

# LOGS

@app.get("/logs")
def logs(
    session: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):

    logs = list_logs(session)

    return {
        "logs": logs,
        "message": "Loaded logs."
    }