# app/main.py
from fastapi import FastAPI
from app.apis.v1.endpoints import api_v1_router

app = FastAPI()

app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
