from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///database.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

event.listen(engine, "connect", lambda conn, rec: conn.execute("PRAGMA foreign_keys=ON"))
