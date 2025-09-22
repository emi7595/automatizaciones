from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="MVP Automatizaciones")

app.include_router(routes.router)

@app.get("/")
def root():
    return {"msg": "API funcionando 🚀"}