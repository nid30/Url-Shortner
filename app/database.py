import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://shortener:shortener@localhost:5432/shortener"
)

# echo=True is handy while you're learning the SQL being generated;
# turn it off once you trust the ORM.
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create tables if they don't exist. Fine for a portfolio project;
    a 'real' project would use Alembic migrations instead — see the
    alembic/ folder we'll add in the next phase."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency — yields a DB session per request and
    closes it automatically afterward."""
    with Session(engine) as session:
        yield session
