from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserCreate, UserOut, Token, TokenData
from app.models.audit import AuditLog
from app.services.email_service import send_email
import uuid
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
@router.post("/reset-password-request")
def reset_password_request(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = str(uuid.uuid4())
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    email_body = f"Please click the following link to reset your password: {reset_link}"
    send_email(email, "LexVellum Password Reset Request", email_body)
    audit_log = AuditLog(
        user_id=user.id,
        user_name=user.full_name or user.email,
        action="Password Reset Requested",
        original_text="N/A",
        new_text=f"User requested a password reset link to {email}"
    )
    db.add(audit_log)
    db.commit()
    return {"message": "If this email is registered, a reset link will be sent."}
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
def check_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return role_checker
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
@router.post("/users", response_model=UserOut)
def create_managed_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db), 
    current_ceo: User = Depends(check_role(["CEO"]))
):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    email_body = f"An account has been created for you with the role of {user_in.role}. Please log in using your email."
    send_email(user_in.email, "Welcome to LexVellum Differential", email_body)
    audit_log = AuditLog(
        user_id=current_ceo.id,
        user_name=current_ceo.full_name or current_ceo.email,
        action="Created User Account",
        original_text="N/A",
        new_text=f"Created {user_in.role} account for {user_in.email}"
    )
    db.add(audit_log)
    db.commit()
    return new_user
@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db), 
    current_ceo: User = Depends(check_role(["CEO"]))
):
    return db.query(User).all()
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_ceo: User = Depends(check_role(["CEO"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email == current_ceo.email:
        raise HTTPException(status_code=400, detail="CEO cannot delete themselves")
    db.delete(user)
    audit_log = AuditLog(
        user_id=current_ceo.id,
        user_name=current_ceo.full_name or current_ceo.email,
        action="Deleted User Account",
        original_text=f"Deleted account: {user.email}",
        new_text="N/A"
    )
    db.add(audit_log)
    db.commit()
    return None
@router.put("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int, 
    new_password: str, 
    db: Session = Depends(get_db), 
    current_ceo: User = Depends(check_role(["CEO"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    audit_log = AuditLog(
        user_id=current_ceo.id,
        user_name=current_ceo.full_name or current_ceo.email,
        action="Manual Password Reset",
        original_text="N/A",
        new_text=f"CEO manually reset password for {user.email}"
    )
    db.add(audit_log)
    db.commit()
    return {"message": "Password reset successfully"}
