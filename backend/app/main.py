from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.rag_router import router as rag_router

app = FastAPI(
    title="LexVellum Differential API",
    description="AI-driven strategic legal compliance engine",
    version="0.1.0",
)

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

@app.get("/")
async def root():
    return {"message": "Welcome to LexVellum Differential API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
