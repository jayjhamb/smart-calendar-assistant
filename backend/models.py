from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///data.db', echo=False, future=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, future=True)

class UserToken(Base):
    __tablename__ = 'user_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    credentials = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)
