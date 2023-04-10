from fastapi import FastAPI
from users import router as allusers
from text import router as textclassif


app = FastAPI()

app.include_router(allusers)
app.include_router(textclassif)
