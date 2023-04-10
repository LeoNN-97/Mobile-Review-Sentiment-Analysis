from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Create a database URL for SQLAlchemy
#DATABASE_URL = "postgresql://postgres:goodleo48@localhost:5432/imuploadpg"          
DATABASE_URL ="postgresql://ut0ztscbg7bwh430opt8:TzulfsMyKjm0U8kuXK0wV9lrl523h8@b2hubzeul8olahp6fwol-postgresql.services.clever-cloud.com:5432/b2hubzeul8olahp6fwol"
# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
# Create a Base class
Base = declarative_base()