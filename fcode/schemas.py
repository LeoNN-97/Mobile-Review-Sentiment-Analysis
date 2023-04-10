from pydantic import BaseModel, FileUrl,EmailStr,validator
from fastapi import Depends, FastAPI,APIRouter,HTTPException,status
import re
import uuid
class UserIn(BaseModel):
    username: str
    email: str
    password: str
    place:str

    @validator("password")
    def validate_password(cls, password):
        # Put your validations here
        errors = []
        if not any(character.islower() for character in password):
            errors.append('Password should contain at least one lowercase character.')
        if not any(character.isupper() for character in password):
            errors.append('Password should contain at least one Upper case character.')
        if not re.search('[0-9]',password):
            errors.append('Password should contain digits.')
        if not re.search('[^\w\s]',password):
            errors.append('Password should special characters.')
        if errors:
            # logger.errors("password validation Error while User Registration:",errors)
            raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=errors)
        return password

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    place:str
    
    class Config:
        orm_mode = True

class reviewuploads(BaseModel):
    id: uuid.UUID
    url: FileUrl
    Content_type: str
    Status: int

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str