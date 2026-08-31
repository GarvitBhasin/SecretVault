from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.database import Role, SessionLocal, Users
from backend.helpers import raise_error
from backend.security import validate_user, verify_user


# Attempt db connection
# Yield db and catch any exceptions
# Perform cleanup (db.close()) at end of enpoint function
def get_db():
    try:
        db = SessionLocal()

        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Extract token from auth header
# Raise appropriate error if auth header invalid/missing
# Use token to decode user_id and expiry
# Raise appropriate error for expired/invalid/tampered token or malformed sub
# Check if user exists
# Return user object
def get_user(request: Request, session: Session = Depends(get_db)):
    auth = request.headers.get("Authorization")

    if not auth:
        raise_error(401, "Authorization token missing.")

    if not auth.startswith("Bearer "):
        raise_error(401, "Invalid authorization format.")

    return verify_user(auth.removeprefix("Bearer "), session)


# Use existing dependencies to:
#   - Connect to db
#   - Extract user_id and perform other security checks mentioned above
# Extract user_id's role
# Compare role's acces level (using Role enum) to minimum access level provided
# Return user's role/appropriate error
def require_role(minimum_access_role: Role):
    def checkrole(session: Session = Depends(get_db), user: Users = Depends(get_user)):
        validate_user(session, user, minimum_access_role)
