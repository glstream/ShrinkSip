# main.py
from fastapi import FastAPI, Depends
from routers import auth,users, drinking_windows

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(drinking_windows.router)

# GET ROUTES
@app.get("/")
def read_root():
    return {"message": "Welcome to the Drinking Cessation App API"}
