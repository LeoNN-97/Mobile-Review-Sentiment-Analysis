from sqlalchemy import Boolean, Column, Integer, String,JSON
from database import Base
import uuid
from sqlalchemy import Column, String, update ,Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# Create SQLAlchemy models from the Base class

class User(Base):
    __tablename__ = "users"
    # Create model attributes/columns
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    place = Column(String)

class review1(Base):
    __tablename__ = "review_sa"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String)
    user = Column(String)
    data = Column(String)
    Status = Column(Integer)