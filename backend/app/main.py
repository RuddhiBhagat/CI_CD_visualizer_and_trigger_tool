from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pipelines, repos  
from app.database.db import engine
from app.models.pipeline import Base
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(pipelines.router)
app.include_router(repos.router) 
