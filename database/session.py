from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///database.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
