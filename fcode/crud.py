from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union,List
import uuid
from database import engine
from transformers import pipeline
import pandas as pd
from jose import JWTError, jwt
from fastapi import HTTPException,status,Depends
import models, schemas
import logging


from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',
                    filename='users&text_logging.log',filemode='w')


def get_users(db: Session):
    return db.query(models.User).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def change_password(db: Session,username,plainpassword:str,newpassword:str):
    chuser=db.query(models.User).filter(models.User.username == username).first()
    if chuser:
        schemas.UserIn.validate_password(newpassword)
        if verify_password(plainpassword, chuser.password):
            chdb=db.query(models.User).filter(models.User.username == username).update({models.User.password:pwd_context.hash(newpassword)}, synchronize_session=False)
            db.commit()
            return chdb
        else :
            return False
    else:
        return False
    

def delete_user(db: Session,username):
    deldb=db.query(models.User).filter(models.User.username == username).first()
    delusername=deldb.username
    db.delete(deldb)
    db.commit()
    return delusername

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserIn):
    db_user = models.User(username = user.username, email=user.email ,password=pwd_context.hash(user.password),place=user.place)
    db.add(db_user) # add that instance object to your database session
    db.commit() # commit the changes to the database (so that they are saved).
    db.refresh(db_user) # refresh your instance
    return db_user

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def getpath(db: Session,newid:uuid):
    return db.query(models.review1).filter(models.review1.id == newid).first()

def find_user(db:Session,token:str):
    newpayload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username= newpayload.get("sub")
    return username

def create_review_table(db: Session,mainpath:str,usern:str):
    db_user = models.review1(url=mainpath,user=usern,data="null", Status=0)
    db.add(db_user)  
    db.commit()  
    db.refresh(db_user)  
    logger.info("Table for storing csv and status Created")
    return db_user

def review_table_getid(db: Session,mainpath:str):
    # idd=db.query(models.review1.id).filter(models.review1.url == mainpath).first()['id']
    obj = db.query(models.review1).all()
    return obj[-1].id

def task_success(db: Session,id:uuid,csvjson):
    try:
        db.query(models.review1).filter(models.review1.id == id).update({models.review1.data:csvjson,models.review1.Status:1}, synchronize_session=False)
        db.commit()
    except Exception:
        logger.error("DB Rolled Error in update if senteiment analysis is success")
        db.rollback()
    return "Sucess"

def task_failed(db: Session,id:uuid):
    try:
        db.query(models.review1).filter(models.review1.id == id).update({models.review1.Status:2}, synchronize_session=False)
        db.commit()
    except Exception:
        logger.error("DB Rolled Error in update if senteiment analysis is Failed")
        db.rollback()
    return "Failed"

def status_check(db: Session,id:uuid):
    statuser=db.query(models.review1).filter(models.review1.id == id).first()
    statusvalue=statuser.Status
    

    return statusvalue
    
def authenticate_user(fake_db, username: str, password: str):
    user = get_user_by_username(fake_db, username)
    if not user:
        logger.error("Username is Wrong")
        return False
    if not verify_password(password, user.password):
        logger.error("password is Wrong")
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=20)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_token(db: Session,token: str ):                                   
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Incorrect Token")
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        logger.error("Incorrect Token")
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)                
    if user is None:
        logger.error("Incorrect Token")
        raise credentials_exception
    return "user"

