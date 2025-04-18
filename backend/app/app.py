from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database
import os
from .routers import users, problems, submissions, auth
from . import initial_data

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

# Initialize default data
initial_data.init_db()

app = FastAPI(title="Consultigo API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Consultigo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(problems.router)
app.include_router(submissions.router) 