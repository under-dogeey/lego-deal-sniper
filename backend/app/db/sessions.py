from app.core.config import settings
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker


engine = create_engine(settings.database_url, echo=True, connect_args={"connect_timeout": 5})

session_factory = sessionmaker(bind=engine)





