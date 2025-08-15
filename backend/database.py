from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class DbMain :
    
    def __init__(self):
        DATABASE_URL = "sqlite:///./app.db"
        self.engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False})
        self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.Base = declarative_base()

    def get_base(self):
        return self.Base
    
    def get_engine(self):
        return self.engine
    
    def get_session(self):
        return self.session

dbmain = DbMain()

Base =  dbmain.get_base()
DBEngine = dbmain.get_engine()
SessionLocal = dbmain.get_session()