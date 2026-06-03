from fastapi import FastAPI

from app.api.v1 import admin, auth, users

app = FastAPI(title="Auth System", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
