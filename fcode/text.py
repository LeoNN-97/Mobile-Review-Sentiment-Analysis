import sqlalchemy, shutil, databases,os

from typing import List
from fastapi import  UploadFile,APIRouter,File, UploadFile, Request, BackgroundTasks,HTTPException,Depends
from transformers import pipeline
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
from sqlalchemy.orm import Session
import crud, models
import uuid
from crud import logger

from database import SessionLocal, engine

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error("DB Rolled back due to Invalid Transaction in Text part:",e)
        # raise e
    finally:
        db.close()

try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.critical('Failed to connect to database: %s', e)
    
def sentiment(idd:uuid,db: Session = Depends(get_db)):
    print("Sentiment  Analysis is running")
    dbitem=crud.getpath(db,idd).url
    csvdf=pd.read_csv(dbitem)

    classifier = pipeline("sentiment-analysis",model="distilbert-base-uncased-finetuned-sst-2-english")
    try:
        reviews = [r[:512] for r in csvdf['Reviews']]
        review_pred=classifier(reviews)
        preds=[item['label'] for item in list(review_pred)]
        # print(preds)
        csvdf['rating_pred']=preds
        csvjson = csvdf[['Product Name','Reviews','Review Votes','rating_pred']].to_json()
        crud.task_success(db,idd,csvjson)
        print("sentiment-analysis model has Completed the Task")
    except Exception as e:
        logger.debug("Error in Sentiment-Analysis",e)
        crud.task_failed(db,idd)
        print("Error while Running Sentiment Analysis Model\nError:",e)


fpath=os.getcwd().replace("\\", "/")


@router.post("/uploadfile/",tags=['Upload Csv File'])
def create_upload_file(background_tasks: BackgroundTasks,token:str=Depends(oauth2_scheme),db: Session = Depends(get_db),file: UploadFile = File(...)):
     
    crud.validate_token(db,token)
    with open(f"{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    fname = file.filename
    mainpath = fpath + '/' + fname
    usern=crud.find_user(db,token)
    if not file:
        logger.error("No file input")
        return "No file sent", 400    
    else:
       
        crud.create_review_table(db,mainpath,usern)
        idd = crud.review_table_getid(db,mainpath)

    
    background_tasks.add_task(sentiment,idd,db)
    logger.info("Background Task Completed and Status updated in DB")
    return {"ID":idd}

@router.get("/status/", tags=['check status and return result'])
async def dbstatus(idd:uuid.UUID,token:str=Depends(oauth2_scheme),db: Session = Depends(get_db)):
    crud.validate_token(db,token)
    statusvalue=crud.status_check(db,idd)
    logger.info("Status value accessed")

    if statusvalue == 1:
        sval = "success"
        logger.info("status is Success")
    elif statusvalue == 0:
        sval = "progressing"
        logger.info("status is Progressing")
    else:
        sval = "failed"
        logger.info("status is Failed")

    return {"Status": sval}

