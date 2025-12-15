import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Optional

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'database.db')
engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

event.listen(engine, "connect", lambda conn, rec: conn.execute("PRAGMA foreign_keys=ON"))


# Global singleton session instance
_global_session: Optional[Session] = None


def get_session() -> Session:
	"""
	Get or create a global singleton database session.

	This session is meant for scripts and utilities that need a long-lived session.
	Use scoped_session() context manager if you need automatic cleanup.

	Returns:
		Session: The global database session
	"""
	global _global_session
	if _global_session is None:
		_global_session = SessionLocal()
	return _global_session


def close_global_session():
	"""
	Close the global singleton session if it exists.
	Should be called at the end of scripts/programs.
	"""
	global _global_session
	if _global_session is not None:
		_global_session.close()
		_global_session = None


@contextmanager
def scoped_session():
	"""
	Context manager that provides a database session with automatic cleanup.

	Usage:
		with scoped_session() as session:
			# use session
			session.query(...)

	The session will be automatically closed when exiting the context.
	"""
	session = SessionLocal()
	try:
		yield session
		session.commit()
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()
