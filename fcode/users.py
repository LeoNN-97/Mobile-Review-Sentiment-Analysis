from typing import Union,List
from datetime import datetime, timedelta
from fastapi import Depends, FastAPI,APIRouter,HTTPException,status,Response
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from crud import logger
router = APIRouter()




SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 50




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error("DB Rolled back due to Invalid Transaction in users part",e)
        # raise e
    finally:
        db.close()
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.critical('Failed to connect to database: %s', e)



@router.post("/create/user/", response_model=schemas.User,tags=['User login Registration'])
def create_user(user: schemas.UserIn, db: Session =Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.debug("Username already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    # try:
    #     returned_user=crud.create_user(db=db, user=user)
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=e)
    returned_user=crud.create_user(db=db, user=user)
    logger.info("User created")
    return Response(content=f" User {returned_user.username} is Registered",headers={"Content-Type": "text/html"},status_code=201)

@router.get("/get/users/", response_model=List[schemas.User],tags=['List of Users'])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

@router.post("/token",response_model=schemas.Token,tags=['Token Generation'])
async def login_for_access_token(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error("Incorrect username or password for Token Generation")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    logger.info("Token created Successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/changepass", response_model=List[schemas.User],tags=['Change user password'])
def changepass(username:str,password:str,newpassword:str,db: Session = Depends(get_db)):
    chusers = crud.change_password(db,username,password,newpassword)
    if chusers:
        logger.info("Password updated Successfully")
        return Response(content=f" Password  has been Updated",headers={"Content-Type": "text/html"},status_code=200)
    else: 
        logger.error("Incorrect Username/Password Entered ")
        return Response(content=f"Incorrect Username/Password ",headers={"Content-Type": "text/html"},status_code=401)

@router.delete("/delete", response_model=List[schemas.User],tags=['Delete user'])
def delete(username:str,db: Session = Depends(get_db)):
    delusers = crud.delete_user(db,username)
    logger.info("User deleted Successfully")
    return Response(content=f" User {delusers} has been Deleted",headers={"Content-Type": "text/html"},status_code=200)