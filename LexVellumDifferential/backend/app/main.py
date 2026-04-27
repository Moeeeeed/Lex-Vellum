from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.rag_router import router as rag_router
from app.api.auth_router import router as auth_router, get_password_hash
from app.core.database import engine, get_db
from app.models.base import Base
from app.models.user import User
from app.core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LexVellum Differential API",
    description="AI-driven strategic legal compliance engine",
    version="0.1.0",
)

@app.on_event("startup")
def create_ceo_user():
    db = next(get_db())
    ceo = db.query(User).filter(User.email == settings.CEO_EMAIL).first()
    if not ceo:
        print(f"Creating CEO: {settings.CEO_EMAIL}")
        print(f"Password length: {len(settings.CEO_PASSWORD)}")
        hashed_password = get_password_hash(settings.CEO_PASSWORD)
        ceo = User(
            email=settings.CEO_EMAIL,
            full_name="LexVellum CEO",
            hashed_password=hashed_password,
            role="CEO"
        )
        db.add(ceo)
        db.commit()
        print(f"CEO user created: {settings.CEO_EMAIL}")

# Configure CORS for React frontend
# In production, replace "*" with the actual origin of the React app
origins = [
    "http://localhost:5173",  # Default Vite React port
    "http://localhost:3000",  # Default Create React App port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to LexVellum Differential API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
