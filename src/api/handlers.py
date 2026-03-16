from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/profile/")
def who_i_am():
    return {"message": "I am profile service!"}
    
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})
