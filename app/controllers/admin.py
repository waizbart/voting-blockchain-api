from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.admin import AdminLogin, Token
from app.db.config import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.admin import Admin

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db, settings.SECRET_KEY)


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    admin = auth_service.get_current_user(token)
    if admin is None:
        raise credentials_exception

    return admin


@router.post("/admin/login", response_model=Token)
def login(
    admin_data: AdminLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    admin = auth_service.authenticate_user(
        admin_data.username, admin_data.password)
    if not admin:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    access_token = auth_service.create_access_token(
        data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}
