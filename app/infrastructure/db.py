from sqlmodel import SQLModel, create_engine, Session

from env import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

def add_to_db(session: Session, item: SQLModel):
    session.add(item)
    session.commit()
    session.refresh(item)

def delete_from_db(session: Session, item: SQLModel):
    session.delete(item)
    session.commit()
    session.refresh(item)
