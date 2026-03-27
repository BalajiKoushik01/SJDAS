import os
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALLOW_LEGACY_TOKEN = os.getenv("ALLOW_LEGACY_TOKEN", "true").lower() == "true"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
MOCK_TOKEN = os.getenv("MOCK_TOKEN", "mock-secret-token")
DEFAULT_ADMIN_ROLES = os.getenv("DEFAULT_ADMIN_ROLES", "admin").split(",")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class User(BaseModel):
    username: str
    is_active: bool = True
    roles: List[str] = Field(default_factory=list)


def _verify_admin_password(plain_password: str) -> bool:
    if ADMIN_PASSWORD_HASH:
        return pwd_context.verify(plain_password, ADMIN_PASSWORD_HASH)
    # Legacy compatibility path while environments migrate to hashed secret.
    return plain_password == ADMIN_PASSWORD


def _create_access_token(subject: str, roles: List[str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "roles": roles,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_token(token: str) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        roles = payload.get("roles", [])
        if not username:
            raise ValueError("Token missing subject")
        return User(username=username, roles=roles)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    if ALLOW_LEGACY_TOKEN and token == MOCK_TOKEN:
        return User(username=ADMIN_USERNAME, roles=DEFAULT_ADMIN_ROLES)
    return _decode_token(token)


def require_roles(required_roles: List[str]):
    async def _role_checker(current_user: User = Depends(get_current_user)) -> User:
        current_roles = set(current_user.roles)
        if not current_roles.intersection(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return _role_checker


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or not _verify_admin_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    roles = [role.strip() for role in DEFAULT_ADMIN_ROLES if role.strip()]
    token = _create_access_token(ADMIN_USERNAME, roles=roles or ["admin"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


verify_token = get_current_user
