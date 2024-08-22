from fastapi import FastAPI
from routers import route_todo
from schemas import SuccessMessage
app = FastAPI()
app.include_router(route_todo.router)
@app.get("/", response_model=SuccessMessage)
def _root():
    return {"message": "Welcome to the FastAPI!"}