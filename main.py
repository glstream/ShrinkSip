# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from routers import auth,users, drinking_windows, drinks

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(drinking_windows.router)
app.include_router(drinks.router)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

# GET ROUTES
@app.get("/")
def read_root():
    return {"message": "Welcome to the Drinking Cessation App API"}
