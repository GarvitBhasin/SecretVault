import pytest
from backend.database import CreateProjectRequest, Projects
from backend.main import create_project

def test_project_is_created(db_session, admin):
    token = encode_token({"sub": str(admin.id)})

    result = create_project(
        CreateProjectRequest(
            token=token,
            name="Test Project"
        )
    )

    assert result["message"] == "Created project."