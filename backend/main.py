from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from backend.database import Role, Users
from backend.dependencies import get_db, get_user, require_role
from backend.requests import (
    AddUserRequest,
    DeleteSelfRequest,
    EditUserRequest,
    InitRequest,
    LoginRequest,
    NameRequest,
    ResetPasswordRequest,
    SecretInfoRequest,
)
from backend.services.auth.delete_self import delete_self
from backend.services.auth.initialize import initialize_vault
from backend.services.auth.login import login_user
from backend.services.auth.reset_password import reset_password
from backend.services.logs.list_logs import list_logs
from backend.services.projects.create_project import create_project
from backend.services.projects.delete_project import delete_project
from backend.services.projects.edit_project import edit_project
from backend.services.projects.list_projects import list_projects
from backend.services.secrets.create_secret import create_secret
from backend.services.secrets.delete_secret import delete_secret
from backend.services.secrets.edit_secret import edit_secret
from backend.services.secrets.get_secret import get_secret
from backend.services.secrets.list_secrets import list_secrets
from backend.services.users.create_user import create_user
from backend.services.users.delete_user import delete_user
from backend.services.users.edit_user import edit_user
from backend.services.users.list_users import list_users

app = FastAPI()

# INIT


@app.post("/init", status_code=201)
def init(data: InitRequest, session: Session = Depends(get_db)):

    initialize_vault(data.username, data.email, data.password, data.confirm, session)

    session.commit()

    return {
        "message": "Owner account created. You can now log in with your credentials."
    }


# AUTH


@app.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_db)):

    token = login_user(data.email, data.password, session)

    return {"token": token, "token_type": "bearer", "message": "Logged in."}


@app.get("/me")
def me(user: Users = Depends(get_user)):
    return (
        f"Loaded user details.\n"
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Role: {user.role.lower()}"
    )


@app.delete("/delete-self")
def delete_self_account(
    data: DeleteSelfRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
):

    delete_self(data.password, user, session)

    session.commit()

    return {"message": "Deleted account."}


@app.patch("/reset-password")
def reset_pass(
    data: ResetPasswordRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
):

    reset_password(data.password, data.confirm, user, session)

    session.commit()

    return {"message": "Password reset successfully."}


# USER


@app.post("/user", status_code=201)
def create_usr(
    data: AddUserRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.ADMIN)),
):

    create_user(
        data.username, data.email, data.password, data.confirm, data.role, user, session
    )

    session.commit()

    return {"message": "Created account."}


@app.delete("/user/{deletion_id}")
def delete_usr(
    deletion_id: int,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.OWNER)),
):

    delete_user(deletion_id, user, session)

    session.commit()

    return {"message": "Account deleted successfully."}


@app.patch("/user/{editing_id}")
def edit_usr(
    editing_id: int,
    data: EditUserRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.OWNER)),
):

    edit_user(editing_id, data.role, user, session)

    session.commit()

    return {"message": "Updated user role."}


@app.get("/users")
def list_usrs(session: Session = Depends(get_db), user: Users = Depends(get_user)):

    users = list_users(session)

    return {"users": users, "message": "Loaded users."}


# PROJECTS


@app.post("/projects", status_code=201)
def create_proj(
    data: NameRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.ADMIN)),
):

    create_project(data.name, user, session)

    session.commit()

    return {"message": "Created project."}


@app.delete("/projects/{project_id}")
def delete_proj(
    project_id: int,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.OWNER)),
):

    delete_project(project_id, user, session)

    session.commit()

    return {"message": "Deleted project."}


@app.patch("/projects/{project_id}")
def edit_proj(
    project_id: int,
    data: NameRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.ADMIN)),
):

    edit_project(data.name, project_id, user, session)

    session.commit()

    return {"message": "Edited project."}


@app.get("/projects")
def list_proj(session: Session = Depends(get_db), user: Users = Depends(get_user)):

    projects = list_projects(session)

    return {"projects": projects, "message": "Loaded projects."}


# SECRETS


@app.post("/projects/{project_id}/secrets", status_code=201)
def create_sec(
    project_id: int,
    data: SecretInfoRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.ADMIN)),
):

    create_secret(project_id, data.name, data.description, data.value, user, session)

    session.commit()

    return {"message": "Created secret."}


@app.delete("/secrets/{secret_id}")
def delete_sec(
    secret_id: int,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.OWNER)),
):

    delete_secret(secret_id, user, session)

    session.commit()

    return {"message": "Deleted secret."}


@app.patch("/secrets/{secret_id}")
def edit_sec(
    secret_id: int,
    data: SecretInfoRequest,
    session: Session = Depends(get_db),
    user: Users = Depends(get_user),
    _: None = Depends(require_role(Role.ADMIN)),
):

    edit_secret(secret_id, data.name, data.value, data.description, user, session)

    session.commit()

    return {"message": "Edited secret."}


@app.get("/projects/{project_id}/secrets")
def list_sec(
    project_id: int, session: Session = Depends(get_db), user: Users = Depends(get_user)
):

    secrets = list_secrets(project_id, session)

    return {"secrets": secrets, "message": "Loaded secrets."}


@app.get("/secrets/{secret_id}")
def get_sec(
    secret_id: int, session: Session = Depends(get_db), user: Users = Depends(get_user)
):

    secret = get_secret(secret_id, user, session)

    session.commit()

    return {"secret": secret, "message": "Loaded secret."}


# LOGS


@app.get("/logs")
def logs(session: Session = Depends(get_db), user: Users = Depends(get_user)):

    logs = list_logs(session)

    return {"logs": logs, "message": "Loaded logs."}
