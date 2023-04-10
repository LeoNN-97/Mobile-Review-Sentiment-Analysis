from fastapi.testclient import TestClient
from crud import *
from fastapi import FastAPI,Depends
from main import app
import pytest
from database import SessionLocal, engine
client = TestClient(app)




@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




def test_create_user_username_already_exists(db:Session):

    
    # user = {
    #     "username": "username123",
    #     "email" : 'user23@gmail.com',
    #     "password": "Newestpassword123#",
    #     'place': "TVM1"
    
    # }
    # response = client.post("/create/user/", json=user)

  
    assert  get_user_by_username(db, username='username123')


def test_validate_token(db: Session ):
    ACCESS_TOKEN_EXPIRE_MINUTES = 5
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    valid_token = create_access_token(data={"sub":'username123'}, expires_delta=access_token_expires)
    # validate_token(db,valid_token)

    assert validate_token(db,valid_token) == "user"


def test_validate_none_token(db: Session):
    invalid_tocken = 'eyJhbGciO45444444qpEIORVTki4'
    with pytest.raises(HTTPException) as val:
        validate_token(db,invalid_tocken)
    assert val.value.detail == 'Could not validate credentials'

